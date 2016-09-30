# Configuration for the Facebook group archiver script

# not required but used to create the access token.
app_id = "111222"
app_secret = "abc123"

# the token used to query data from the FB graph api.
access_token = "%s|%s" % (app_id, app_secret)

# Fields in query
fields = "comments.limit(1000){message,like_count,created_time,from},from,message,created_time,full_picture,link,updated_time,caption,source,likes,permalink_url"

