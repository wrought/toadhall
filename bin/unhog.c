#include <unistd.h>

int main(int argc, char* argv[])
{
    char cmd[100];
    char ipaddr[20];
    char* c;
    char* d;

    if (argc < 2) exit(1);
    d = ipaddr;
    for (c = argv[1]; *c; c++) {
        if (*c == '.') *d++ = *c;
        if (*c >= '0' && *c <= '9') *d++ = *c;
        if (d > ipaddr + 18) break;
    }
    *d = 0;
    sprintf(cmd, "/sbin/ipchains -D hog -s %s -j REJECT", ipaddr);
    system(cmd);
}
