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
        TOC = 'toc' # nodes relative to parent and root is src-dir


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
                TOC,
            ],
            PROJECT_DOC_LATEX: [
                SRC_DIR,
                BUILD_DIR,
                QUICK,
                PATHS_TO_COPY,
                DEFAULT_TEMPLATE,
                PDF_PATH,
                TOC,
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
    SERVICE_WORKER = 'worker'
    SERVICE_ = [
        SERVICE_NEW,
        SERVICE_BUILD,
        SERVICE_WORKER,
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

class BUILD:
    MAP_PROJECT_EXTENSION = {
        CLI.PROJECT_SERVER_PHP: '.php',
        CLI.PROJECT_MARSHAL_DART: '.dart',
        CLI.PROJECT_DOC_HTML: '.html',
        CLI.PROJECT_DOC_LATEX: '.tex',
    }

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

class WORKER_CONFIG:
    class KEY:
        CALENDAR                 = 'calendar'
        LOGS                     = 'logs'
        JOBS                     = 'jobs'
        _ = [
            CALENDAR,
            LOGS,
            JOBS,
        ]

        LOGS_DIR                 = 'dir'
        LOGS_LIFETIME            = 'lifetime'      # in days
        LOGS_ = [
            LOGS_DIR,
            LOGS_LIFETIME,
        ]

        JOBS_METHOD               = 'method'
        JOBS_RESOURCE             = 'resource'
        JOBS_REQUEST              = 'request'
        JOBS_ALLOW_OVERLAP        = 'allowOverlap'
        JOBS_STORE_LOGS           = 'storeLogs'
        JOBS_EVERY                = 'every'
        JOBS_ = [
            JOBS_METHOD,
            JOBS_RESOURCE,
            JOBS_REQUEST,
            JOBS_ALLOW_OVERLAP,
            JOBS_STORE_LOGS,
            JOBS_EVERY,
        ]

        JOBS_EVERY_NUMBER         = 'number'
        JOBS_EVERY_UNIT           = 'unit'
        JOBS_EVERY_AT             = 'at'            # starting from 1 step lower than unit
        JOBS_EVERY_ = [
            JOBS_EVERY_NUMBER,
            JOBS_EVERY_UNIT,
            JOBS_EVERY_AT,
        ]

    class VALUE:
        class CALENDAR:
            JALALI = 'jalali'
            GREGORIAN = 'gregorian'
            _ = [
                JALALI,
                GREGORIAN,
            ]

        class JOBS_METHOD:
            GET = 'GET'
            POST = 'POST'
            _ = [
                GET,
                POST,
            ]

        class JOBS_EVERY_UNIT:
            SECOND  = 'second'
            MINUTE  = 'minute'
            HOUR    = 'hour'
            DAY     = 'day'
            WEEK    = 'week'
            MONTH   = 'month'
            QUARTER = 'quarter'
            YEAR    = 'year'
            _ = [
                SECOND,
                MINUTE,
                HOUR,
                DAY,
                WEEK,
                MONTH,
                QUARTER,
                YEAR,
            ]

            AT_LIMIT = {
                MINUTE:  lambda number, calendar: [0, 60 * number - 1],
                HOUR:    lambda number, calendar: [0, 60 * number - 1],
                DAY:     lambda number, calendar: [0, 24 * number - 1],
                WEEK:    lambda number, calendar: [1, 7 * number],
                MONTH:   lambda number, calendar: [1, 28 * number] if calendar == 'gregorian' else [1, 29 * number],
                QUARTER: lambda number, calendar: [1, 3 * number],
                YEAR:    lambda number, calendar: [1, 12 * number],
            }

            LOWER = {
                MINUTE:  SECOND,
                HOUR:    MINUTE,
                DAY:     HOUR,
                WEEK:    DAY,
                MONTH:   DAY,
                QUARTER: MONTH,
                YEAR:    MONTH,
            }

        def DEFAULT_():
            return {
                WORKER_CONFIG.KEY.CALENDAR: WORKER_CONFIG.VALUE.CALENDAR.GREGORIAN,
                WORKER_CONFIG.KEY.LOGS: {},

                WORKER_CONFIG.KEY.LOGS_DIR: 'logs',
                WORKER_CONFIG.KEY.LOGS_LIFETIME: '30',

                WORKER_CONFIG.KEY.JOBS_METHOD: WORKER_CONFIG.VALUE.JOBS_METHOD.POST,
                WORKER_CONFIG.KEY.JOBS_REQUEST: {},
                WORKER_CONFIG.KEY.JOBS_ALLOW_OVERLAP: True,
                WORKER_CONFIG.KEY.JOBS_STORE_LOGS: False,

                WORKER_CONFIG.KEY.JOBS_EVERY_AT: ['0'],
            }