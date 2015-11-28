# -*- coding: utf-8 -*-
"""
myapp.application
=================
This is the main entry point for your app. It contains the app factory.

:copyright: (C) 2011, Matthew Frazier
:license:   MIT/X11, see LICENSE for details
"""
from flask import Flask, url_for, request, session, redirect
from flask.ext.oauth import OAuth
from .views import BLUEPRINTS

def create_app(config=None, extras=None):
    # create application object
    app = Flask("sakulaci")
    
    # configure application
    app.config.from_object("sakulaci.defaults")
    if isinstance(config, dict):
        app.config.update(config)
    elif isinstance(config, str):
        app.config.from_pyfile(config)
    if isinstance(extras, dict):
        # extras is primarily for the use of the ep.io launcher
        app.config.update(extras)
    
    # setup extensions
    
    for blueprint in BLUEPRINTS:
        if isinstance(blueprint, tuple):
            app.register_blueprint(blueprint[0], url_prefix=blueprint[1])
        else:
            app.register_blueprint(blueprint)
    
    # template utilities, etc.
    
    oauth = OAuth()

    facebook = oauth.remote_app('facebook',
        base_url = 'https://graph.facebook.com/',
        request_token_url = None,
        access_token_url = '/oauth/access_token',
        authorize_url = 'https://www.facebook.com/dialog/oauth',
        consumer_key = app.config['FACEBOOK_APP_ID'],
        consumer_secret = app.config['FACEBOOK_APP_SECRET'],
        request_token_params = { 'scope': 'email' }
    )

    @app.route('/login/facebook')
    def login_facebook():
        return facebook.authorize(callback=url_for('facebook_authorized',
                                 next=request.args.get('next') or request.referrer or None,
                                 _external=True))

    @app.route('/login/facebook/authorized')
    @facebook.authorized_handler
    def facebook_authorized(resp):
        if resp is None:
            return 'Access denied: reason=%s errr=%s' % (
                request.args['error_reason'],
                request.args['error_description']
            )
        session['oauth_token'] = (resp['access_token'], '')
        me = facebook.get('/me')
        return 'Logged in as id=%s name=%s email=%s redirect=%s' % \
                (me.data['id'], me.data['name'], me.data['email'], request.args.get('next'))

    @facebook.tokengetter
    def get_facebook_oauth_token():
        return session.get('oauth_token')


    twitter = oauth.remote_app('twitter',
                               base_url = 'http://api.twiter.com/1/',
                               request_token_url = 'https://api.twitter.com/oauth/request_token',
                               access_token_url = 'https://api.twitter.com/oauth/access_token',
                               authorize_url = 'https://api.twitter.com/oauth/authorize',
                              consumer_key = app.config['TWITTER_CONSUMER_KEY'],
                              consumer_secret = app.config['TWITTER_CONSUMER_SECRET'])

    @twitter.tokengetter
    def get_twitter_token():
        return session.get('twitter_token')

    @app.route('/login/twitter')
    def login_twitter():
        return twitter.authorize(
            callback=url_for('twitter_authorized', 
            next=request.args.get('next') or request.referrer or None))

    @app.route('/oauth-authorized')
    @twitter.authorized_handler
    def twitter_authorized(resp):
        next_url = request.args.get('next') or '/'
        if resp is None:
            return 'Access denied: reason=%s errr=%s' % (
                request.args['error_reason'],
                request.args['error_description']
            )
        session['oauth_token'] = (resp['oauth_token'], resp['oauth_token_secret'])
        return 'Signed in as (screenname): %s' % resp['screen_name']


    @app.route('/logout')
    def logout():
        session.pop('outh_token', None)
        return redirect('/')

    app.jinja_env.add_extension('pyjade.ext.jinja.PyJadeExtension')
    return app
