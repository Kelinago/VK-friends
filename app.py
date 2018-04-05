# coding=utf-8
from flask import Flask, render_template, redirect, url_for, request, session
import requests
import json
import os

app = Flask(__name__)
app.SESSION_TYPE = 'redis'
app.secret_key = os.urandom(24)
app.config.from_object(__name__)

vk_config = json.load(open('config.json'))


def handle_error(error, error_description):
    # Filter access errors
    if error == 'access_denied' or error == '5':
        error = 'Ошибка доступа'
        error_description = 'Для продолжения необходимо авторизоваться ' \
                            'и предоставить доступ к общей информации'
        session.pop('user_id', None)

    return render_template('index.html', error=error, error_description=error_description)


@app.route('/')
def home():
    error = request.args.get('error')
    if error:
        error_description = request.args.get('error_description')
        return handle_error(error, error_description)

    if session.get('user_id'):
        return redirect(url_for('friends'))

    code = request.args.get('code')
    if code:
        access_token_uri = vk_config['ACCESS_TOKEN_URI_TEMPLATE'].format(vk_config['APP_ID'], vk_config['APP_CODE'],
                                                                         vk_config['VK_API_REDIRECT_URI'], code)
        access_response = json.loads(requests.get(access_token_uri).text)

        if 'error' in access_response:
            return handle_error(error=access_response.get('error'),
                                error_description=access_response.get('error_description'))

        user_info_uri = vk_config['USER_INFO_URI_TEMPLATE']\
            .format(access_response['user_id'], access_response['access_token'], vk_config['VK_API_VERSION'])

        user_info_response = json.loads(requests.get(user_info_uri).text)
        error = user_info_response.get('error')
        if error and error.get('error_code'):
            return handle_error(error=access_response.get('error'),
                                error_description=access_response.get('error_description'))

        # Just save all necessary information in our session
        session['user_id'] = access_response['user_id']
        session['full_name'] = ' '.join((user_info_response['response'][0]['first_name'],
                                         user_info_response['response'][0]['last_name']))
        session['access_token'] = access_response['access_token']
        return redirect(url_for('friends'))

    return render_template('index.html')


@app.route('/friends')
def friends():
    if not session.get('user_id'):
        return redirect(url_for('home'))

    friends_link = vk_config['FRIENDS_URI_TEMPLATE'].format(session['user_id'], 'random', 5, 'photo_100,online',
                                                            session['access_token'], vk_config['VK_API_VERSION'])

    friendlist_response = json.loads(requests.get(friends_link).text)
    error = friendlist_response.get('error')

    if error and error.get('error_code'):
        return redirect(url_for('home', error=error.get('error_code', None),
                                error_description=error.get('error_msg', None)))

    return render_template('friends.html',
                           user_id=session['user_id'],
                           full_name=session['full_name'],
                           friendlist=friendlist_response['response']['items'])


if __name__ == '__main__':
    app.run(debug=True)
