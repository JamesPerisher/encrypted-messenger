# client library
slixmpp

## encrytion
use gpg etc

aloow communication if a user is granted the public key

## future
XEP-0084: User Avatar

## user sync (future)
XEP-0048: Bookmarks

XEP-0049: Private XML Storage

XEP-0313: Message Archive Management


## notes
XEP-0231: Bits of Binary


# updating username-colour
we can use the change username to change the nick of the user 

thus giving `Username-#999999` etc


# allow multiuser groupchat
xmpp.register_plugin('xep_0045')


# running the server

## run daemon
```bash
sudo dockerd
```

## run docker
### start new
```bash
sudo docker run --name ejabberd -p 5222:5222 ejabberd/ecs
```
### just restart it
```bash
sudo docker start ejabberd
```

## create user
```bash
sudo docker exec -it ejabberd bin/ejabberdctl register user1 localhost password
sudo docker exec -it ejabberd bin/ejabberdctl register user2 localhost password
```