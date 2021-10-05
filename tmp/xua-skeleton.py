import os


class Xua:
    def __init__(rootDir=None):
        """Initialize an instance of class Xua.

        Args:
            rootDir (str): Path of root directory of the xua project. Defaults to os.getcwd().
        """

        if not dir:
            dir = os.getcwd()
        os.chdir(rootDir)

    # #  #  #  #  #  #  #  #  #  #  #  #  #  #  #
    # T E M P L A T E S
    # #  #  #  #  #  #  #  #  #  #  #  #  #  #  #
    def templateProject(self):
        """Creates a template project in the current working directory.

        Raises:
            Exception: If the directory is not empty, raises "Directory is not empty".

        Returns:
            list: A list of all created files.
        """

        # TODO implement
        return []

    def templateSuper(self):
        """Generates template content for xua Super.

        Returns:
            str: The content of the template file
        """

        # TODO implement
        return ''

    def templateEntity(self):
        """Generates template content for xua Entity.

        Returns:
            str: The content of the template file
        """

        # TODO implement
        return ''

    def templateMethod(self):
        """Generates template content for xua Method.

        Returns:
            str: The content of the template file
        """

        # TODO implement
        return ''

    def templateService(self, lang='php'):
        """Generates template content for xua Service.

        Args:
            lang (str, optional): The language of the service. Defaults to 'php'.

        Returns:
            str: The content of the template file
        """

        # TODO implement
        return ''

    def templateInterface(self):
        """Generates template content for xua Interface.

        Returns:
            str: The content of the template file
        """

        # TODO implement
        return ''

    # #  #  #  #  #  #  #  #  #  #  #  #  #  #  #
    # B U I L D
    # #  #  #  #  #  #  #  #  #  #  #  #  #  #  #
    def buildBase(self, project):
        """Builds the base of the resulting project. The created files are guaranteed to be inside the folder PROJECT-DEST-DIR/XUA, the only
        exception is for server/php project which has another file PROJECT-DEST-DIR/index.php.

        Args:
            project (str): The resulting project name, one of values:
                'server/php',
                'marshal/dart', 'marshal/java', 'marshal/javascript', 'marshal/kotlin', 'marshal/objectivec', 'marshal/swift',
                'doc/latex', 'doc/html',

        Returns:
            list: A list of all created files.
        """

        # TODO implement
        return []

    def buildBaseSingular(self, project, filename):
        """Just like the Xua.buildBase method but builds only one file of the base. Efficient when only some of the base files are corrupt. 

        Args:
            project (str): The resulting project name, one of values:
                'server/php',
                'marshal/dart', 'marshal/java', 'marshal/javascript', 'marshal/kotlin', 'marshal/objectivec', 'marshal/swift',
                'doc/latex', 'doc/html',
            filename (str): path of the file that needs to be rebuilt, relative to the project destination directory.

        """

        # TODO implement
        return

    def buildSingular(self, project, filename):
        """builds a single file into a project.

        Args:
            project (str): The resulting project name, one of values:
                'server/php',
                'marshal/dart', 'marshal/java', 'marshal/javascript', 'marshal/kotlin', 'marshal/objectivec', 'marshal/swift',
                'doc/latex', 'doc/html',
            filename (str): path of the source file that needs to be built.

        Returns:
            list: A list of built files generated from the source file.
        """

        # TODO implement
        return []
