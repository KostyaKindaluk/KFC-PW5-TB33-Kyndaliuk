DB_USERNAME = "root"
DB_PASSWORD = "superqwerty123!"
DB_HOST = "localhost"
DB_PORT = 3306
DB_NAME = "tsp_ga"

DATABASE_URL = (
  f"mysql+mysqldb://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)


TRAINING_CITY_COUNT = 60