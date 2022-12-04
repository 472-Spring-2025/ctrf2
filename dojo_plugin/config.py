import sqlalchemy
import warnings
import logging
import os

from CTFd.models import db, Admins, Pages, Flags, Challenges
from CTFd.cache import cache
from CTFd.utils import config, set_config
from .utils import multiprocess_lock

_LOG = logging.getLogger(__name__)

VIRTUAL_HOST = os.getenv("VIRTUAL_HOST")
HOST_DATA_PATH = os.getenv("HOST_DATA_PATH")
DISCORD_CLIENT_ID = os.getenv("DISCORD_CLIENT_ID")
DISCORD_CLIENT_SECRET = os.getenv("DISCORD_CLIENT_SECRET")
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
DISCORD_GUILD_ID = os.getenv("DISCORD_GUILD_ID")
BINARY_NINJA_API_KEY = os.getenv("BINARY_NINJA_API_KEY")

missing_errors = ["VIRTUAL_HOST", "HOST_DATA_PATH"]
missing_warnings = ["DISCORD_CLIENT_ID", "DISCORD_CLIENT_SECRET", "DISCORD_BOT_TOKEN", "DISCORD_GUILD_ID", "BINARY_NINJA_API_KEY"]

for config_option in missing_errors:
    config_value = globals()[config_option]
    if not config_value:
        raise RuntimeError(f"Configuration Error: {config_option} must be set in the environment")

for config_option in missing_warnings:
    config_value = globals()[config_option]
    if not config_value:
        warnings.warn(f"Configuration Warning: {config_option} is not set in the environment")

def load_dojo(dojo_id, dojo_spec, user="global"):
    from .models import DojoChallenges, Dojos

    dojo_log = logging.getLogger(f"dojos.{user}.{dojo_id}")
    dojo_log.info("Initiating dojo load.")

    dojo = Dojos.query.filter_by(id=dojo_id).first()
    if not dojo:
        dojo = Dojos(id=dojo_id)
        dojo_log.info("Dojo is new, adding.")
        db.session.add(dojo)
    elif dojo.data == dojo_spec:
        dojo_log.info("Dojo is unchanged, aborting update.")
        return

    dojo.data = dojo_spec
    db.session.commit()

    assert dojo.config.get("dojo_spec", None) == "v2"

    # delete all challenges owned by this dojo
    dojo_log.info("Deleting existing challenge mappings.")
    deleter = sqlalchemy.delete(DojoChallenges).where(DojoChallenges.dojo_id == dojo.id).execution_options(synchronize_session="fetch")
    db.session.execute(deleter)
    db.session.commit()

    # re-load the dojo challenges
    for module_idx,module in enumerate(dojo.config["modules"], start=1):
        if "name" not in module:
            dojo_log.info("Module index %d is missing 'name' field; skipping.", module_idx)
            continue

        if "challenges" not in module:
            dojo_log.info("Module %s has no challenges defined. Skipping challenge load.", module["name"])
            continue

        dojo_log.info("Loading challenges for module %s.", module["name"])

        for level_idx,challenge_spec in enumerate(module["challenges"], start=1):
            dojo_log.info("Loading module %s challenge %d", module["name"], level_idx)
            description = challenge_spec.get("description", None)

            # spec dependent
            category = None
            provider_dojo_id = None
            provider_module = None

            if "import" not in challenge_spec:
                if "name" not in challenge_spec:
                    dojo_log.info("... challenge is missing a name. Skipping.")
                    continue

                # if this is our dojo's challenge, make sure it's in the DB
                name = challenge_spec["name"]
                category = challenge_spec.get("category", f"{dojo.id}-challenge")

                dojo_log.info("... challenge name: %s", name)

                challenge = Challenges.query.filter_by(
                    name=name, category=category
                ).first()
                if not challenge:
                    dojo_log.info("... challenge is new; creating")
                    challenge = Challenges(
                        name=name,
                        category=category,
                        value=1,
                        state="visible",
                    )
                    db.session.add(challenge)
                    db.session.commit()

                    flag = Flags(challenge_id=challenge.id, type="dojo")
                    db.session.add(flag)
                    db.session.commit()
                elif description is not None and challenge.description != description:
                    dojo_log.info("... challenge already exists; updating description")
                    challenge.description = description
                    db.session.commit()
            else:
                if challenge_spec["import"].count("/") != 2:
                    dojo_log.info("... malformed import statement, should be dojo_id/module_name/challenge_name. Skipping.")
                    continue

                # if we're importing this from another dojo, do that
                provider_dojo_id, provider_module, provider_challenge = challenge_spec["import"].split("/")
                dojo_log.info("... importing from dojo %s, module %s, challenge %s", provider_dojo_id, provider_module, name)

                provider_dojo_challenge = (
                    DojoChallenges.query
                    .join(Challenges, Challenges.id == DojoChallenges.challenge_id)
                    .filter(
                        DojoChallenges.dojo_id==provider_dojo_id, DojoChallenges.module==provider_module,
                        Challenges.name==provider_challenge
                    )
                ).first()
                if not provider_dojo_challenge:
                    dojo_log.info("... can't find provider challenge; skipping")
                    continue

                challenge = provider_dojo_challenge.challenge

            dojo_log.info("... creating dojo-challenge link for challenge %d", level_idx)
            # then create the DojoChallenge link
            dojo_challenge = DojoChallenges(
                challenge_id=challenge.id,
                dojo_id=dojo.id,
                provider_dojo_id=provider_dojo_id,
                provider_module=provider_module,
                level_idx=level_idx,
                module_idx=module_idx,
                description_override=description,
                assigned_date=module.get("time_assigned", None),
                module=module["id"],
                docker_image_name="pwncollege-challenge",
            )
            db.session.add(dojo_challenge)

    db.session.commit()


@multiprocess_lock
def bootstrap():
    from .pages.discord import discord_reputation
    from .utils import CHALLENGES_DIR, DOJOS_DIR

    set_config("ctf_name", "pwn.college")
    set_config("ctf_description", "pwn.college")
    set_config("user_mode", "users")

    set_config("challenge_visibility", "public")
    set_config("registration_visibility", "public")
    set_config("score_visibility", "public")
    set_config("account_visibility", "public")

    set_config("ctf_theme", "dojo_theme")

    set_config("mailfrom_addr", f"hacker@{VIRTUAL_HOST}")
    set_config("mail_server", f"mailserver")
    set_config("mail_port", 587)
    set_config("mail_useauth", True)
    set_config("mail_username", f"hacker@{VIRTUAL_HOST}")
    set_config("mail_password", "hacker")

    memes_path = CHALLENGES_DIR / "memes.yml"
    memes = memes_path.read_text() if memes_path.exists() else "[]"
    set_config("memes", memes)

    cache.delete_memoized(discord_reputation)
    discord_reputation()

    if not config.is_setup():
        admin_password = os.urandom(8).hex()
        admin = Admins(
            name="admin",
            email="admin@example.com",
            password=admin_password,
            type="admin",
            hidden=True,
        )
        page = Pages(title=None, route="index", content="", draft=False)

        db.session.add(admin)
        db.session.add(page)
        db.session.commit()

        with open("/var/data/initial_credentials", "w") as f:
            f.write(f"admin:{admin_password}\n")

        set_config("setup", True)

    for dojo_config_path in DOJOS_DIR.glob("*.yml"):
        _LOG.info("Loading dojo specification %s", dojo_config_path)
        dojo_id = dojo_config_path.stem
        spec = dojo_config_path.read_text()
        load_dojo(dojo_id, spec)
