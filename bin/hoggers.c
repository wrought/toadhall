#include <unistd.h>

int main(int argc, char* argv[])
{
    system("/sbin/ipchains -n -L hog");
}
