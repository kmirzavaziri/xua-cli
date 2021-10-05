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

        BUILD_DIR        = 'build-dir'
        QUICK            = 'quick'
        PATHS_TO_COPY    = 'paths-to-copy'

        COMPATIBLE_WITH  = 'compatible-with'
        DEFAULT_TEMPLATE = 'default-template'


        PROJECT_KEY_ = {
            PROJECT_SERVER_PHP: [
                BUILD_DIR,
                QUICK,
                PATHS_TO_COPY,
                COMPATIBLE_WITH,
            ],
            PROJECT_MARSHAL_DART: [
                BUILD_DIR,
                QUICK,
                PATHS_TO_COPY,
            ],
            PROJECT_DOC_HTML: [
                BUILD_DIR,
                QUICK,
                PATHS_TO_COPY,
                DEFAULT_TEMPLATE,
            ],
            PROJECT_DOC_LATEX: [
                BUILD_DIR,
                QUICK,
                PATHS_TO_COPY,
                DEFAULT_TEMPLATE,
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
                if compatibleWith == COMPATIBLE_WITH.NGINX:
                    return 'var/www'
                elif compatibleWith == COMPATIBLE_WITH.APACHE:
                    return 'public_html'
                elif compatibleWith == COMPATIBLE_WITH.BUILT_IN:
                    return 'php'
                elif compatibleWith == COMPATIBLE_WITH.COMPOSER:
                    return 'src'
            except KeyError:
                pass
            return 'php'

        def DEFAULT_():
            return {
                CONFIG.KEY.PROJECT_SERVER_PHP: {
                    CONFIG.KEY.BUILD_DIR: lambda c: 'build/' + defaultPhpDestination(c),
                    CONFIG.KEY.COMPATIBLE_WITH: CONFIG.VALUE.COMPATIBLE_WITH.BUILT_IN,
                },
                CONFIG.KEY.PROJECT_MARSHAL_DART: {
                    CONFIG.KEY.BUILD_DIR: 'build/marshal/dart',
                },
                CONFIG.KEY.PROJECT_DOC_HTML: {
                    CONFIG.KEY.BUILD_DIR: 'build/doc/html',
                },
                CONFIG.KEY.PROJECT_DOC_LATEX: {
                    CONFIG.KEY.BUILD_DIR: 'build/doc/latex',
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