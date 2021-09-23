import os

from XuaTools import XuaTools as XT

cliDir = os.path.dirname(os.path.realpath(__file__))

xuaArgs = XT.xuaArgParse()

if xuaArgs.service == 'build':
    buildArgs = XT.xuaBuildArgParse(xuaArgs.args[0])

    if not buildArgs.filename:
        buildArgs.filename = os.getcwd()

    buildArgs.filename = os.path.abspath(buildArgs.filename)

    projectDir = XT.getProjectDir(buildArgs.filename)
    if projectDir == None:
        raise Exception(
            "Cannot find root directory of the project. Please add a file named '.__xua_root__' to root directory.")
    xt = XT(projectDir)

    if os.path.isfile(buildArgs.filename):
        if buildArgs.filename.endswith(".xua"):
            xt.build(buildArgs.filename)
        else:
            xt.copy(buildArgs.filename)
            # @TODO think
    elif os.path.isdir(buildArgs.filename):
        # XT.buildBase(buildArgs.filename)

        for subdir, dirs, files in os.walk(buildArgs.filename):
            for file in files:
                filename = os.path.join(subdir, file)
                if filename.endswith(".xua"):
                    xt.build(filename)

if xuaArgs.service == 'new':
    print("shit")
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
