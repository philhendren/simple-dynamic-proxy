from flask import Flask, request, jsonify, redirect
import requests

app = Flask(__name__)

# Store routes in a dictionary
routes = {}

# Reverse proxy handler
@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH'])
def proxy(path):
    if path in routes:
        target_url = routes[path]
        response = requests.request(
            method=request.method,
            url=f'{target_url}/{path}',
            headers={key: value for key, value in request.headers if key != 'Host'},
            data=request.get_data(),
            cookies=request.cookies,
            allow_redirects=False
        )
        headers = [(name, value) for name, value in response.raw.headers.items()]
        return (response.content, response.status_code, headers)
    else:
        return "Route not found", 404

# API to add new routes
@app.route('/api/add_route', methods=['POST'])
def add_route():
    data = request.json
    if 'route' in data and 'target' in data:
        routes[data['route']] = data['target']
        return jsonify({'message': 'Route added', 'route': data['route'], 'target': data['target']}), 201
    else:
        return jsonify({'error': 'Invalid request, route and target required'}), 400

# API to list all routes
@app.route('/api/routes', methods=['GET'])
def list_routes():
    return jsonify(routes)

# API to delete a route
@app.route('/api/delete_route', methods=['DELETE'])
def delete_route():
    data = request.json
    if 'route' in data:
        removed_target = routes.pop(data['route'], None)
        if removed_target:
            return jsonify({'message': 'Route removed', 'route': data['route']}), 200
        else:
            return jsonify({'error': 'Route not found'}), 404
    else:
        return jsonify({'error': 'Invalid request, route required'}), 400

if __name__ == '__main__':
    app.run(debug=True)

