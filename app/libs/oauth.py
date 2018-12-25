# from app.extensions import oauth
# from flask import current_app, url_for, request, redirect, session
#
# class GoogleSignIn():
#     def __init__(self):
#         self.service = oauth.remote_app(
#             'google',
#             consumer_key=current_app.config.get('GOOGLE_ID'),
#             consumer_secret=current_app.config.get('GOOGLE_SECRET'),
#             request_token_params={
#                 'scope': 'email'
#             },
#             base_url='https://www.googleapis.com/oauth2/v1/',
#             request_token_url=None,
#             access_token_method='POST',
#             access_token_url='https://accounts.google.com/o/oauth2/token',
#             authorize_url='https://accounts.google.com/o/oauth2/auth',
#         )
#         self.service.tokengetter(self.get_oauth2_token)
#
#     def authorization(self):
#         """
#         Building the authorization request url is done using Flask-OAuthlib's
#         authorize(). To sign in with Google, we will call into authorize()
#         and pass it the URL that the user should be redirected back to.
#         It returns a redirect response to the remote authorization URL with
#         the signed callback given.
#         The response_type=code argument tells the OAuth provider
#         that the application is a web application. Finally, the redirect_uri
#         argument is set to the application route that the provider needs
#         to invoke after it completes the authentication.
#         This Google redirect_uri should not have a next appended to it.
#         """
#         return self.service.authorize(
#             callback=self.get_redirect_uri())
#
#     def authorized(self):
#         """
#         If the application redirects back, the remote application can fetch
#         all relevant information in the oauth_authorized function with
#         authorized_response(). Google returns an access_token like this:
#         {'access_token': 'x', 'expires_in': 3600, 'id_token': 'x',
#         'token_type': 'Bearer'}
#
#         Returns:
#             provider, social_id, email_address, username
#         """
#         resp = self.service.authorized_response()
#         # resp = {'access_token': 'x', 'expires_in': 3600, 'id_token': 'x',
#         #   'token_type': 'Bearer'}
#         if resp is None or resp.get('access_token') is None:
#             return redirect(url_for('gw.index'))
#         session['oauth2_token'] = (resp['access_token'], '')
#         # https://developers.google.com/oauthplayground
#         userinfo = self.service.request(
#             'https://www.googleapis.com/userinfo/v2/me')
#         # userinfo.data = {'name': 'Johan Soetens', 'id': 'x', 'email': 'x'}
#         email_address, username = None, None
#         provider = 'Google'
#         social_id = userinfo.data.get('id')
#         if userinfo.data.get('email'):
#             email_address = userinfo.data.get('email')
#         if userinfo.data.get('name'):
#             username = userinfo.data.get('name')
#         return provider, social_id, email_address, username
#
#     def get_oauth2_token(self, token=None):
#         """
#         Register a function as token getter.
#         OAuth uses a token and a secret to figure out who is connecting to the
#         remote application. After authentication/authorization this information
#         is passed to a function on our side and we need to remember it.
#         If the token does not exist, the function must return None, and
#         otherwise return a tuple in the form (token, secret). The function
#         might also be passed a token parameter. This is user defined and can
#         be used to indicate another token.
#         The name of the token can be passed to to the request() function.
#         """
#         return session.get('oauth2_token')
#
#     def get_redirect_uri(self):
#         """
#         The get_redirect_uri() method builds the redirect_uri based on
#         the provider name. It is meant to be provided to the authorize()
#         method. We add the argument _external=True to method url_for()
#         so it will return us an absolute url.
#         Atm not using next=request.args.get('next') or request.referrer or None
#
#         Returns:
#             Absolute path for redirect_uri
#         """
#         return url_for('gw.authorized', _external=True)
#
#
