#define FUSE_USE_VERSION 30

#include <fuse.h>
#include <string.h>
#include <stdio.h>
#include <errno.h>
#include <unistd.h>
#include <sys/types.h>

static int workspace_getattr(const char *path, struct stat *stbuf)
{
    if (strcmp(path, "/") == 0) {
        stbuf->st_mode = S_IFDIR | 0755;
        stbuf->st_nlink = 2;
        return 0;
    }

    uid_t uid = fuse_get_context()->uid;
    if (uid != 1000)
        return -ENOENT;

    memset(stbuf, 0, sizeof(struct stat));
    stbuf->st_mode = S_IFLNK | 0777;
    stbuf->st_nlink = 1;
    stbuf->st_uid = 0;
    stbuf->st_gid = 0;
    stbuf->st_size = strlen("/run/dojo/bin") + strlen(path);
    return 0;
}

static int workspace_readdir(const char *path, void *buf, fuse_fill_dir_t filler, off_t offset, struct fuse_file_info *fi)
{
    if (strcmp(path, "/") != 0) {
        return -ENOENT;
    }

    filler(buf, ".", NULL, 0);
    filler(buf, "..", NULL, 0);

    return 0;
}

static int workspace_readlink(const char *path, char *buf, size_t size)
{
    uid_t uid = fuse_get_context()->uid;
    if (uid != 1000)
        return -ENOENT;

    snprintf(buf, size, "/run/dojo/bin%s", path);
    return 0;
}

static struct fuse_operations workspace_operations = {
    .getattr  = workspace_getattr,
    .readdir  = workspace_readdir,
    .readlink = workspace_readlink,
};

int main(int argc, char *argv[])
{
    return fuse_main(argc, argv, &workspace_operations, NULL);
}
