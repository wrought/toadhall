from commands import getoutput

cache = {}

def local(ipaddr):
    return ipaddr.startswith('10.')

def output(command):
    return getoutput(command).split('\n')

def ipaddrs(command):
    results = []
    for line in output(command):
        words = line.split()
        if words: results.append(words[0])
    return results

def all():
    key = 'all'
    if key not in cache:
        cache[key] = filter(local, ipaddrs("nmblookup '*'"))
    return cache[key]

def masters():
    key = 'masters'
    if key not in cache:
        cache[key] = filter(local, ipaddrs("nmblookup -M -"))
    return cache[key]

def allnames(ipaddrs):
    addrs = [addr for addr in ipaddrs if ('names', addr) not in cache]
    for line in output('nmblookup -d 1 -A %s' % ' '.join(addrs)):
        words = line.split()
        if words[-3:-1] == ['status', 'of']:
            ipaddr = words[-1]
            cache[('names', ipaddr)] = names = {}
        if line.startswith('\t'):
            name = line.split()[0]
            type = line.split('<')[1].split('>')[0].lower()
            if '<GROUP>' in line.split(): type += '*'
            names[type] = name
    results = {}
    for addr in ipaddrs:
        results[addr] = cache[('names', addr)]
    return results

def names(ipaddr):
    key = ('names', ipaddr)
    if key not in cache:
        results = {}
        for line in output('nmblookup -d 1 -A %s' % ipaddr):
            if line.startswith('\t'):
                name = line.split()[0]
                type = line.split('<')[1].split('>')[0].lower()
                if '<GROUP>' in line.split(): type += '*'
                results[type] = name
        cache[key] = results
    return cache[key]

def name(ipaddr):
    return names(ipaddr)['00']

def group(ipaddr):
    return names(ipaddr)['00*']

def groups():
    key = 'groups'
    if key not in cache:
        cache[key] = [group(ipaddr) for ipaddr in masters()]
    return cache[key]

if __name__ == '__main__':
    print 'all', all()
    print 'names', allnames(all())
    print 'master', masters()
    print 'groups', groups()
    print 
    for ipaddr in all():
        print ipaddr
        pairs = names(ipaddr).items()
        pairs.sort()
        for type, name in pairs:
            print '    %-5s %s' % (type, name)
