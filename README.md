# Introduction

DGF is a framework for streamlining the writting process using django and graphene.

<h2> Disclaimer </h2>

This package was initally created for personal project, so it may lack general features you need or have unnecesarry features that you don't need. If you find any of these feel free to leave a issue on [github](https://github.com/LonguCodes/DGF)

# Dependencies

This package requires you to install _graphene_ and _django_

`pip install graphene django`

# Basics

DGF allows you to give easy acces to your models through graphql.

Let's assume we have a model `Profile`

```python
# models.py

from django.db.models import Model,CharField


class Profile(Model):
    first_name = CharField(max_lenght=20)
    last_name = CharField(max_lenght=20)
```

We can easily transform it to graphql-accessable model by creating a schema

```python
# schema.py

from DGF import Schema
from .models import Profile

class ProfileSchema(Schema):
    class Meta:
        model = Profile
```

We specify the information in `Meta` class. The `model` field determines of which model is the schema of.

After that we have to register the schema, so it can be transformed info graphene's schema

We create a combiner and the register the schema

```python
# schema.py

from DGF import Schema, Combiner
from .models import Profile

class ProfileSchema(Schema):
    class Meta:
        model = Profile

combiner = Combiner()
combiner.register(ProfileSchema)
schema = combiner.to_schema()
```

The `schema` can be used like any other graphene schema.

**!!! DGF has not built-in endpoint for graphql as of now !!!**

# Requests

The schema will generate `query` for the model and `add`, `change` and `delete` mutations.

**Filter parameters** are in form of `(lowercase) _<Name of the field>`. Relation fields are excluded.

**Value parameteres** are in form of `(lowercase) <Name of the field>`.
Autofields are excluded. Relations can be provided using ids.

**Return values** are in form of `(lowercase) <Name of the field>`.

## Query

The name of the query will the `<Name of your model>Query`. It returns chosen data about the adequate entries.

```graphql
{
  ProfileQuery(_id: 1) {
    id
    first_name
    last_name
  }
}

# Will get information about every profile with id = 1
```

## Mutations

The name of mutation will be `<Name of your Model>{Add,Change,Delete}` depending of the type of mutation you want to use.

**Add** mutation can get `value parameters` for the new database entry. It returns chosed data about the added entry.

```graphql
mutation {
  ProfileAdd(first_name: "Tom") {
    id
    first_name
  }
}

# Will add new profile with first_name = "Tom" and return it's id and first_name
```

**Change** mutation can get `value parameters` for the changed database entry as well as `filter paramters` for which entries to change. It returns chosen data about the changed entries.

```
mutation {
    ProfileChange(_first_name:"Tom", last_name:"Smith"){
        first_name
        last_name
    }
}

# Will change last_name to "Smith" of every profile with name "Tom" and then return first_name and last_name of these profiles.
```

**Delete** mutation can get `filter paramteres` for which entries to delete. It returns ids of the deleted entries (will return chosen data in future versions).

```
mutation {
    ProfileDelete(_last_name:"Smith")
}

# Will delete every entry with last_name = "Smith" and return the ids of these entries.
# Note the lack of {}
```

# Custom request handling

You can specify which requests should be possible by overriding `allowed_requests`.

```python
from DGF import Schema, QUERY, ADD
from .models import Profile

allowed_requests = [QUERY,ADD]

class ProfileSchema(Schema):
    class Meta:
        model = Profile
```

You can specify which fields should be accessable by adding `fields` field in `Meta` class of the schema.

```python
# schema.py

from DGF import Schema
from .models import Profile

class ProfileSchema(Schema):
    class Meta:
        model = Profile
        fields = ['first_name','id']

```

If `fields` is not defined, all fields will be added.

You can also add your own fields to the schema.

```python
# schema.py
from graphene import Int
from DGF import Schema, Field
from .models import Profile

class ProfileSchema(Schema):
    age = Field(name='age',field=Int()) # The name is required

    class Meta:
        model = Profile
        fields = ['first_name','id','age']

```

If `fields` is not defined, all custom fields will be added. Custom fields will override fields from the model with the same name.

## Custom request logic

Custom fields have to be handled by custom request logic. To add custom request logic you can override a method in the schema.

The methods accepts parameters:

- `schema` - to which schema this method refers
- `model` - to which model this method refers
- `data` - data from the previous link in the chain (for more information read [Pipeline](#Pipeline))
- `raw_data` - the raw, unprocessed request
- `params` - additional data (like `schema`, `model`, `raw_data`,`type` and custom data added by the [Pipeline](#pipeline) modules)

### Fetch

Fetch method get the data from the database. Name of the fetch method is in form of `fetch_{query,add,change,delete}`. Fetch should return the model / list of models.

### Execute

Fetch fucntion execute the request on the provided data. Name of the execute method is in form of `execute_{query,add,change,delete}`. Execute should return the same type as the request's type (see [Query](#query) and [Mutations](#mutations))

# Pipeline

DGF has built-in pipeline that let's you customize the behaviour on every step. The default pipeline is composed of:

- `AuthLink` - tries to authenticate the user based on the provided credentials using authenticatos
- `RequestPermissionLink` - checks if the user has permission to make this request
- `FetchLink` - fetches the data from the database about the model
- `ObjectPermissionLink` - filters the data based on the permission the user has
- `ExecuteLink` - executes the request (applies only to `Change` and `Delete` mutations by default)

First link in the pipeline get's the data from graphene, every other gets the data from previous one.

You can change the pipeline by setting `DGF_PIPELINE` in the settings.

```python
# settings.py

DGF_PIPELINE=[
    'DGF.builtins.FetchPipeline',
    'DGF.builtins.ExecutePipeline'
]
# The bare minimum for everything to work out of the box
```

### Auth Link

Addes new param `user` that represents the authenticated user (uses the same model as django). The authentication is done using [Authenticators](#authenticators). If it's not possible to authenticate user, sets `user` to `AnonymousUser`.

### Request Permission Link

Uses [Permissions](#permissions) to check if the user is suppose to use this request. If not, throws `Unauthorized`.

### Fetch Link

Calls fetch method on the schema (see [Fetch](#fetch)).

### Object Permission Link

Uses [Permissions](#permissions) to filter the data.

### Execute Link

Calls execute method on the schema (see [Execute](#execute))

## Custom link

You can create your own link by overriding the `BaseLink` class and the `process` method inside.

```python
# links.py

from DGF import BaseLink

class CustomLink(BaseLink):
    def process(self, data):
        # Your custom logic
        return data
```

You can get and set additional parameters by using `self.params` or `self.context`.

# Auth

## Authenticators

Authenticators allow you to authenticate the user without writting custom backend. Parameters for the authentication can be both in body or headers. By default [Model Authenticator](#model-authenticator) is used.

### Model Authenticator

Model authenticator is used for authenticating the user using username and password. It uses Django's default backend.

### Backend Authenticator

Base class for authenticator, that use existing backends. You need to define `args` field with names of all paramateres needed for authentication and it will call django's `authenticate` to try to authenticate the user

```python
class ModelAuthenticator(BackendAuthenticator):
    args = ['username', 'password']
```

### Bearer Authenticator

Base class for authenticator, that user the Bearer token. You need to override the `authenticate_token` method, which should return the user.

```python
from django.conf import settings
from jwt import decode
from django.contrib.auth import get_user_model
from DGF.builtins import BearerAuthenticator

class JWTAuthenticator(BearerAuthenticator):
    @classmethod
    def authenticate_token(cls, token):
        if not token:
            return None
        try:
            decoded = decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            return get_user_model().objects.get(pk=decoded['sub'])
        except:
            return None
```

### Custom Authenticator

You can write custom authenticator by overriding `BaseAuthenticator` and `authenticate` method inside as well as `args` field.

```python
# authenticators.py
from django.contrib.auth import get_user_model
import DGF.Authenticator

class CustomAuthenticator(BaseAuthenticator):
    args = ['username']

    @classmethod
    def authenticate(cls,username, **kwargs):
        try:
            return get_user_model().objects.get(username=username)
        except:
            return None
```

## Permissions

Permissions allow you to limit the user im terms of requests and particular entries.

You can set permission for each schema by overriding the `permissions` field.

```python
# schema.py
from DGF import Schema
from DGF.builtins import ReadOnlyPermission
from .models import Profile

class ProfileSchema(Schema):
    class Meta:
        model = Profile

    permissions = [ReadOnlyPermission]
```

### Read Only Permission

Allows only `Query` requests.

### Custom permissions

You can write your own permissions by overriding `BasePermissions` class as well as overriding one or more of the methods:

- `has_object_permission` - for [Object Permission Link](#object-permission-link)
- `has_request_permission` - for [Request Permission Link](#request-permission-link)

Both methods can accept `schema`, `model`, `data` and `params`.

```python
# permission.py

from DGF import BasePermission

class IsAuthenticated(BasePermission):
    @staticmethod
    def has_request_permission(params, **kwargs):
        return params['user'].is_authenticated


class IsOwner(BasePermission):
    @staticmethod
    def has_object_permission(schema, data, params, **kwargs):
        return getattr(data,'owner',None) == params['user']

```
