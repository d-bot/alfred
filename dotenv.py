class Dotenv:

    def dotenv():
        with open('.env', 'r') as f:
            for line in f.readlines():
                secrets = line.rstrip().split(':')
        return tuple(secrets)

