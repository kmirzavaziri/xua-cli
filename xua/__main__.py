from xua.tools import *

try:
    Cli.entry()
except UserError as e:
    Logger.log(Logger.ERROR, '', str(e))

# if xuaArgs.service == 'new':
#     print("TODO")
    # xuadoc.run(currentDirectory, args.args)
    # exit()
    # try:
    # if args.service == 'new':
    #     XuaNew(currentDirectory, args.args).run()
    # if args.service == 'build':
    #     XuaBuild(currentDirectory, args.args).run()
    #     if args.service == 'doc':
    #         xuadoc.run(currentDirectory, args.args)
    # except Exception as e:
    #     print("Error:", e)