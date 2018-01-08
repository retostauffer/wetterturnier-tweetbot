import tweepy

def get_api(cfg):
  auth = tweepy.OAuthHandler(cfg['consumer_key'], cfg['consumer_secret'])
  auth.set_access_token(cfg['access_token'], cfg['access_token_secret'])
  return tweepy.API(auth)

def main( apicfg, message, image ):

  api = get_api( apicfg )
  # Pure status
  #status = api.update_status(status=tweet) 
  # With Image
  status = api.update_with_media( image, status = message )
  print status
  # Yes, tweet is called 'status' rather confusing

if __name__ == "__main__":

  # -----------------------------------------------------------------
  # Reading config
  # -----------------------------------------------------------------
  import os, sys, ConfigParser
  if not os.path.isfile( "config.conf" ):
    sys.exit("Sorry, no config file found")
  # Fill in the values noted in previous step here
  CNF = ConfigParser.ConfigParser()
  CNF.read( "config.conf" )

  dbcfg = {
    "host"    : CNF.get("database","host"),
    "user"    : CNF.get("database","user"),
    "passwd"  : CNF.get("database","passwd"),
    "db"      : CNF.get("database","db"),
  }

  apicfg = { 
    "consumer_key"        : CNF.get("twitter config","consumer_key"),
    "consumer_secret"     : CNF.get("twitter config","consumer_secret"),
    "access_token"        : CNF.get("twitter config","access_token"),
    "access_token_secret" : CNF.get("twitter config","access_token_secret")
  }

  # -----------------------------------------------------------------
  # Getting leaders
  # -----------------------------------------------------------------
  import MySQLdb
  db = MySQLdb.connect( host=dbcfg["host"], user=dbcfg["user"], passwd=dbcfg["passwd"], db=dbcfg["db"] ) 

  # Last tournament
  cur = db.cursor()
  cur.execute( "SELECT max(tdate) FROM wp_wetterturnier_betstat;" )
  tdate = int(cur.fetchone()[0])

  # Extracting leaders
  leaders = {}
  for city in range(1,6):

    sql = []
    sql.append("SELECT c.name, u.user_login, b.points, b.tdate FROM wp_wetterturnier_betstat AS b ")
    sql.append("LEFT OUTER JOIN")
    sql.append("wp_wetterturnier_cities AS c ON c.ID = b.cityID LEFT OUTER JOIN")
    sql.append("wp_users AS u ON u.ID = b.userID")
    sql.append("WHERE b.tdate = {0:d} and b.cityID = {1:d} AND" )
    sql.append("b.points = (SELECT max(points) from wp_wetterturnier_betstat where cityID={1:d} and tdate = {0:d})")

    sql = "\n".join( sql ).format( tdate, city )
    cur.execute( sql )

    data = cur.fetchall()
    leaders[data[0][0]] = data

  print leaders
  db.close()


  # -----------------------------------------------------------------
  # The message to send
  # -----------------------------------------------------------------
  message = "Test mit Bild"
  image = "images/test.png"
  import os, sys
  if not os.path.isfile(image): sys.exit("file not found")
  main( apicfg, message, image )



