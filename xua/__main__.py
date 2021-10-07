from xua import helpers
from xua import cli
from xua.exceptions import UserError

try:
    cli.entry()
except UserError as e:
    helpers.Logger.log(helpers.Logger.ERROR, '', str(e))