import index
import sae.const

sae.const.MYSQL_DB      # 数据库名
sae.const.MYSQL_USER    # 用户名
sae.const.MYSQL_PASS    # 密码
sae.const.MYSQL_HOST    # 主库域名（可读写）
sae.const.MYSQL_PORT    # 端口，类型为<type 'str'>，请根据框架要求自行转换为int
sae.const.MYSQL_HOST_S  # 从库域名（只读）

settings = index.settings
application = index.application