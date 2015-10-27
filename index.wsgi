import index
import sae.const

settings = index.settings
application = index.application

index.server(sae.const.MYSQL_HOST + ':' + sae.const.MYSQL_PORT, sae.const.MYSQL_DB, sae.const.MYSQL_USER, sae.const.MYSQL_PASS)