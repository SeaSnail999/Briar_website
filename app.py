from flask import Flask, jsonify, request, render_template
import json
from markupsafe import escape
from briar_headless import BriarHeadlessClient

app = Flask(__name__)

def load_forums():
    with open('forums.json', 'r') as file:
        data = json.load(file)
    return data

def load_config():
    with open('config.json', 'r') as file:
        config = json.load(file)
    return config

forums_data = load_forums()
config_data = load_config()
briar_client = BriarHeadlessClient(base_url=config_data['base_url'], auth_token=config_data['auth_token'])

@app.route('/', methods=['GET'])
def index():
    query = escape(request.args.get('query', '')).lower()
    sort_by = escape(request.args.get('sort_by', 'last_post_date'))
    forums = forums_data["forums"]

    if query:
        forums = [forum for forum in forums if query in forum["name"].lower()]

    if sort_by == 'first_post_date':
        forums.sort(key=lambda x: (x['first_post_date'] != "Unknown", x['first_post_date'] or "0000-00-00"), reverse=False)
    elif sort_by == 'total_posts':
        forums.sort(key=lambda x: x['total_posts'], reverse=True)
    elif sort_by == 'name_asc':
        forums.sort(key=lambda x: x['name'].lower(), reverse=False)
    elif sort_by == 'name_desc':
        forums.sort(key=lambda x: x['name'].lower(), reverse=True)
    else:
        forums.sort(key=lambda x: (x['last_post_date'] != "Unknown", x['last_post_date'] or "0000-00-00"), reverse=True)

    return render_template('index.html', forums=forums, query=query, sort_by=sort_by)

@app.route('/forums', methods=['GET'])
def get_forums():
    return jsonify(forums_data)

@app.route('/forums/<int:forum_id>', methods=['GET'])
def get_forum(forum_id):
    forum = next((item for item in forums_data["forums"] if item["id"] == forum_id), None)
    return jsonify(forum) if forum else ('', 404)

@app.route('/search', methods=['GET'])
def search():
    query = escape(request.args.get('query', '')).lower()
    matching_forums = [forum for forum in forums_data["forums"] if query in forum["name"].lower()]
    return jsonify(matching_forums)

@app.route('/request', methods=['GET', 'POST'])
def manage():
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'add_contact':
            briar_contact_link = request.form.get('briar_contact_link')
            try:
                response = briar_client.add_contact(briar_contact_link)
                print(f"Successfully added contact: {response}")
            except Exception as e:
                print(f"Error: {e}")
        elif action == 'request_forums':
            name = request.form.get('briar_contact_link_forum')
            contact_id = briar_client.get_contact_id_by_name(name)
            forum_ids = request.form.getlist('forum_ids')
            try:
                for forum in forum_ids:
                    forum_id, forum_name = forum.split('|')
                    forum_id = briar_client.get_forum_id_by_name(forum_name)
                    briar_client.share_forums(contact_id, [forum_id], f"Invitation to join a {forum_name} from briar.retiolus.net")
            except Exception as e:
                print(f"Error: {e}")
            
    return render_template('request.html', briar_link=config_data["briar_link"], forums=forums_data["forums"])

if __name__ == '__main__':
    app.run(debug=True)
