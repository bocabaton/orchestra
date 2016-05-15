import uuid
from django.db import models

class group(models.Model):
    uuid = models.CharField(max_length=20, default='custom_id', help_text='g', unique=True)
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255, default='')
    created = models.DateTimeField(auto_now_add=True, editable=False)

class user(models.Model):
    user_id = models.CharField(max_length=20, unique=True)
    password = models.CharField(max_length=128)
    name = models.CharField(max_length=255, default='')
    state = models.CharField(max_length=20, default='enable')
    email = models.CharField(max_length=255, default='')
    language = models.CharField(max_length=30)
    timezone = models.CharField(max_length=30)
    group = models.ForeignKey('group', to_field='uuid', null=True, blank=True, default=None)
    created = models.DateTimeField(auto_now_add=True, editable=False)

class user_detail(models.Model):
    user = models.ForeignKey('user', to_field='user_id')
    platform = models.CharField(max_length=20, null=True)
    key = models.CharField(max_length=128, null=True)
    value = models.CharField(max_length=256, null=True)

class user_keypair(models.Model):
    user = models.ForeignKey('user', to_field='user_id')
    key_type = models.CharField(max_length=16, null=False)
    name = models.CharField(max_length=32, null=False, unique=True)
    value = models.CharField(max_length=2048, null=False, editable=False)


class token(models.Model):
    user = models.ForeignKey('user', to_field='user_id')
    token = models.UUIDField(default=uuid.uuid4, unique=True)
    created = models.DateTimeField(auto_now_add=True, editable=False)


class portfolio(models.Model):
    portfolio_id = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=1024, null=True, blank=True, default=None)
    owner = models.CharField(max_length=20, null=False)
    created = models.DateTimeField(auto_now_add=True, editable=False)

class product(models.Model):
    product_id = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    portfolio = models.ForeignKey('portfolio', to_field='portfolio_id', null=False)
    name = models.CharField(max_length=100)
    short_description = models.CharField(max_length=1024, null=True, blank=True, default=None)
    description = models.CharField(max_length=5120, null=True, blank=True, default=None)
    provided_by = models.CharField(max_length=100, null=False)
    vendor = models.CharField(max_length=100, null=True)
    created = models.DateTimeField(auto_now_add=True, editable=False)

class product_detail(models.Model):
    uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey('product', to_field='product_id', null=False)
    email = models.CharField(max_length=255, default='')
    support_link = models.CharField(max_length=100)
    support_description = models.CharField(max_length=1024, null=True, blank=True, default=None)

class package(models.Model):
    package_id = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey('product', to_field='product_id', null=False)
    pkg_type = models.CharField(max_length=128, null=True)
    template = models.CharField(max_length=256, null=True)
    version = models.CharField(max_length=30, null=False)
    description = models.CharField(max_length=1024, null=True, blank=True, default=None)
    created = models.DateTimeField(auto_now_add=True, editable=False)

class tag(models.Model):
    uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey('product', to_field='product_id', null=False)
    key = models.CharField(max_length=128, null=True)
    value = models.CharField(max_length=256, null=True)

class stack(models.Model):
    stack_id = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    package = models.ForeignKey('package', to_field='package_id', null=False)
    env = models.CharField(max_length=10240, null=True)
    state = models.CharField(max_length=20, default='builing')
    created = models.DateTimeField(auto_now_add=True, editable=False)
 
############
# Workflow
############
class workflow(models.Model):
    workflow_id = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    template = models.CharField(max_length=256)
    template_type = models.CharField(max_length=128)

class task(models.Model):
    task_id = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=128, null=False)
    workflow = models.ForeignKey('workflow', to_field='workflow_id', null=False)
    task_uri = models.CharField(max_length=256)
    task_type = models.CharField(max_length=128)

############
# Infra
############
class region(models.Model):
    name = models.CharField(max_length=20)
    region_id = models.UUIDField(default=uuid.uuid4, unique=True)

class zone(models.Model):
    name = models.CharField(max_length=20)
    zone_id = models.UUIDField(default=uuid.uuid4, unique=True)
    zone_type = models.CharField(max_length=20, default='aws')
    region = models.ForeignKey('region', to_field='region_id',null=False)

class zone_detail(models.Model):
    zone = models.ForeignKey('zone', to_field='zone_id', null=False)
    key = models.CharField(max_length=128)
    value = models.CharField(max_length=1024)

class server(models.Model):
    zone = models.ForeignKey('zone', to_field='zone_id', null=False)
    server_id = models.UUIDField(default=uuid.uuid4, unique=True)
    name = models.CharField(max_length=20)

class server_info(models.Model):
    server = models.ForeignKey('server', to_field='server_id', null=False)
    key = models.CharField(max_length=128, null=True)
    value = models.CharField(max_length=2500, null=True)


