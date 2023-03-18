from dynaconf import Dynaconf

settings = Dynaconf(
    envvar_prefix="DYNACONF",
    settings_files=['settings.toml', '.secrets.toml'],
)

# `envvar_prefix` = export envvars with `export DYNACONF_FOO=bar`.
# `settings_files` = Load these files in the order.

POSTGRES_URI = f"postgresql://" \
               f"{settings.PG_LOGIN}" \
               f":{settings.PG_PASS}@{settings.PG_HOST}" \
               f"/{settings.PG_DATABASE}"

