import argparse

def run(debug, **kwargs):
    print(debug)

def main():
    parser = argparse.ArgumentParser(add_help=True)

    subparsers = parser.add_subparsers(required=True)
    run_parser = subparsers.add_parser('run', help="Run help")
    run_parser.set_defaults(dispatch=run)
    run_parser.add_argument('-d', '--debug', action='store_true')

    args = parser.parse_args()
    args_dict = vars(args)
    dispatch = args_dict.pop('dispatch')
    dispatch(**args_dict)

if __name__ == '__main__':
    main()
