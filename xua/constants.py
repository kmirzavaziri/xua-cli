class CONFIG:
    XUA_JSON = 'xua.json'

    class KEY:
        PROJECTS = 'projects'

        PROJECT_SERVER_PHP        = 'server/php'
        PROJECT_MARSHAL_DART      = 'marshal/dart'
        PROJECT_DOC_HTML          = 'doc/html'
        PROJECT_DOC_LATEX         = 'doc/latex'
        PROJECT_ = [
            PROJECT_SERVER_PHP,
            PROJECT_MARSHAL_DART,
            PROJECT_DOC_HTML,
            PROJECT_DOC_LATEX,
        ]

        # Shared
        SRC_DIR          = 'src-dir'
        BUILD_DIR        = 'build-dir'
        QUICK            = 'quick'
        PATHS_TO_COPY    = 'paths-to-copy'  # relative to src-dir

        # server/php
        COMPATIBLE_WITH  = 'compatible-with'
        
        # doc/*
        DEFAULT_TEMPLATE = 'default-template' # relative to xua.json 
        PDF_PATH = 'pdf-path' # relative to build-dir


        PROJECT_KEY_ = {
            PROJECT_SERVER_PHP: [
                SRC_DIR,
                BUILD_DIR,
                QUICK,
                PATHS_TO_COPY,
                COMPATIBLE_WITH,
            ],
            PROJECT_MARSHAL_DART: [
                SRC_DIR,
                BUILD_DIR,
                QUICK,
                PATHS_TO_COPY,
            ],
            PROJECT_DOC_HTML: [
                SRC_DIR,
                BUILD_DIR,
                QUICK,
                PATHS_TO_COPY,
                DEFAULT_TEMPLATE,
                PDF_PATH,
            ],
            PROJECT_DOC_LATEX: [
                SRC_DIR,
                BUILD_DIR,
                QUICK,
                PATHS_TO_COPY,
                DEFAULT_TEMPLATE,
                PDF_PATH,
            ],
        }

    class VALUE:
        class COMPATIBLE_WITH:
            NGINX = 'nginx'
            APACHE = 'apache'
            BUILT_IN = 'built-in'
            COMPOSER = 'composer'

        def defaultPhpDestination(config):
            try:
                compatibleWith = config[CONFIG.KEY.PROJECTS][CONFIG.KEY.PROJECT_SERVER_PHP][CONFIG.KEY.COMPATIBLE_WITH]
                if compatibleWith == CONFIG.VALUE.COMPATIBLE_WITH.NGINX:
                    return 'var/www'
                elif compatibleWith == CONFIG.VALUE.COMPATIBLE_WITH.APACHE:
                    return 'public_html'
                elif compatibleWith == CONFIG.VALUE.COMPATIBLE_WITH.BUILT_IN:
                    return 'php'
                elif compatibleWith == CONFIG.VALUE.COMPATIBLE_WITH.COMPOSER:
                    return 'src'
            except KeyError:
                pass
            return 'php'

        def DEFAULT_():
            return {
                CONFIG.KEY.PROJECT_SERVER_PHP: {
                    CONFIG.KEY.BUILD_DIR: lambda c: 'build/' + CONFIG.VALUE.defaultPhpDestination(c),
                    CONFIG.KEY.QUICK: True,
                    CONFIG.KEY.COMPATIBLE_WITH: CONFIG.VALUE.COMPATIBLE_WITH.BUILT_IN,
                },
                CONFIG.KEY.PROJECT_MARSHAL_DART: {
                    CONFIG.KEY.BUILD_DIR: 'build/marshal/dart',
                    CONFIG.KEY.QUICK: False,
                    CONFIG.KEY.PATHS_TO_COPY: ['Services/dart'],
                },
                CONFIG.KEY.PROJECT_DOC_HTML: {
                    CONFIG.KEY.BUILD_DIR: 'build/doc/html',
                    CONFIG.KEY.QUICK: False,
                    CONFIG.KEY.PATHS_TO_COPY: ['assets'],
                    CONFIG.KEY.DEFAULT_TEMPLATE: None,
                    CONFIG.KEY.PDF_PATH: None,
                },
                CONFIG.KEY.PROJECT_DOC_LATEX: {
                    CONFIG.KEY.BUILD_DIR: 'build/doc/latex',
                    CONFIG.KEY.QUICK: False,
                    CONFIG.KEY.PATHS_TO_COPY: ['assets'],
                    CONFIG.KEY.DEFAULT_TEMPLATE: None,
                    CONFIG.KEY.PDF_PATH: None,
                },
            }

class CLI:
    SERVICE_NEW   = 'new'
    SERVICE_BUILD = 'build'
    SERVICE_ = [
        SERVICE_NEW,
        SERVICE_BUILD,
    ]

    PROJECT_INSTRUCTION_ALL   = 'all'
    PROJECT_INSTRUCTION_QUICK = 'quick'
    PROJECT_SERVER_PHP        = 'server/php'
    PROJECT_MARSHAL_DART      = 'marshal/dart'
    # @TODO other marshal projects
    PROJECT_DOC_HTML          = 'doc/html'
    PROJECT_DOC_LATEX         = 'doc/latex'
    PROJECT_ = [
        PROJECT_INSTRUCTION_ALL,
        PROJECT_INSTRUCTION_QUICK,
        PROJECT_SERVER_PHP,
        PROJECT_MARSHAL_DART,
        PROJECT_DOC_HTML,
        PROJECT_DOC_LATEX,
    ]

    TEMPLATE_TYPE_SUPER = 'super'
    TEMPLATE_TYPE_ = [
        TEMPLATE_TYPE_SUPER,
    ]

class XUA:
    HERO = """
      Xua: A PHP Code Generator
      
      ██╗░░██╗██╗░░░██╗░█████╗░
      ╚██╗██╔╝██║░░░██║██╔══██╗
      ░╚███╔╝░██║░░░██║███████║
      ░██╔██╗░██║░░░██║██╔══██║
      ██╔╝╚██╗╚██████╔╝██║░░██║
      ╚═╝░░╚═╝░╚═════╝░╚═╝░░╚═╝
                1.0-β
"""