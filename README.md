# Kryptos


# Packet information

## Packet byte interpretation

Byte | Value
---   |  ---
0 - 2 | Length
2 - 4 | Packet id
4 - n | Data

Where n is the length of the data in bytes (0 to 2^16). Due to this data encoding method it limmits each packet to 65'536 bytes (aproximatly 65kb).


## Packet types

Packet id | Packet typ | Is json packet | Usage
---       | ---        | ---            | ---
   0      | [NAN     ](#pacnan ) | False          | Packet data type for abitrary data
   1      | [PAC.RAP ](#pacrap ) | False          | Request auth packet
   2      | [PAC.ERR ](#pacerr ) | False          | Error with packet
   3      | [PAC.AERR](#pacaerr) | False          | Authentication error
  20      | [PAC.INF ](#pacinf ) | False          | Request user information
  30      | [PAC.AUT ](#pacaut ) | False          | Request authority nodes
  40      | [PAC.MSG ](#pacmsg ) | True           | Send message
  50      | [PAC.CRT ](#paccrt ) | True           | Request account creation or updates
  70      | [PAC.MLT ](#pacmlt ) | True           | Request a list of message id's between 2 users
  80      | [PAC.GMS ](#pacgms ) | True           | Request a specific message
  11      | [PAC.RAPA](#pacrapa) | False          | Random data by server
  21      | [PAC.INFA](#pacinfa) | True           | Responce for INF
  41      | [PAC.MSGA](#pacmsga) | False          | Message aknowlegements
  51      | [PAC.CRTA](#paccrta) | False          | Acknowlege account creation
  71      | [PAC.MLTA](#pacmlta) | True           | List of message id's between 2 users
  81      | [PAC.GMSA](#pacgmsa) | False          | Message data


## Packets data format

### PAC.NAN
`Packet data type for abitrary data`\
data:
  ```Any```
### PAC.RAP
`Request auth packet`\
data:
```None```
### PAC.ERR
`Error with packet`\
data:
```Message```
### PAC.AERR
`Authentication error`\
data:
```Message```
### PAC.INF
`Request user information`\
data:
```User ID```
### PAC.AUT
`Request authority nodes`\
data:
```None```
### PAC.MSG
`Send message`\
data:
```json
{
    "from" : Sending user ID,
    "to"   : Target user ID,
    "data0": Message encrypted with target public key,
    "data1": Message encrypted with senders public key
}
```
### PAC.CRT
`Request account creation or updates`\
data:
```json
{
    "id":User ID,
    "pub": User public key,
    "verify": signed PAC.AUT data
}
```

### PAC.MLT
`Request a list of message id's between 2 users gets all messages that have been sent between user `u1`  and user  `u2`  since  `time\
data:
```json
{
    "u1": Message from user ID,
    "u2": Message Target user ID,
    "time": Unix timestamp
}
```

### PAC.GMS
`Request a specific message`\
data:
```json
{
    "id": Message ID,
    "data": 0 for encrypted for from user, 1 for encrypted for to user 
}
```
### PAC.RAPA
`Random data by server`\
data:
```Random data (default 128 bytes)```
### PAC.INFA
`Responce for INF`\
data:
```json
[
    [
        User ID,
        User name,
        User public key,
        User color
    ]
]
```
### PAC.MSGA
`Message aknowlegements`\
data:
```None```
### PAC.CRTA
`Acknowlege account creation`\
data:
```True/False```
### PAC.MLTA
`List of message id's between 2 users`\
data:
```json
[
    [
        Message creation unix timestamp,
        Message ID,
        Is `u1` the message author
    ]
]
```

### PAC.GMSA
`Message data`\
data:
```Message data```

