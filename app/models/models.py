from tortoise import Model, fields

#testa

class MyModel(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=255)