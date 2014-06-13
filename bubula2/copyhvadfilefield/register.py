models = {}

# add references to models to a dict where they can be looked up by name
def register_translation_with_file_field_models(*addModels):
    for model in addModels: 
        models.update( { model.__name__: model } )