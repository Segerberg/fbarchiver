# Configuration for the Facebook group archiver script

# not required but used to create the access token.
app_id = "111222"
app_secret = "abc123"

# the token used to query data from the FB graph api.
access_token = "%s|%s" % (app_id, app_secret)

# Fields in query
fields = "comments.limit(1){message,like_count,created_time,from,comments{message,from,created_time,like_count,likes,comments{message,from,created_time,like_count,likes}},likes},from,message,created_time,full_picture,link,updated_time,caption,source,likes,permalink_url"
# set to true if media files should be fetched
hydrate_media = False

# Root folder for archive data - data will be created here
data_dir = "/path/to/fbarchive"



