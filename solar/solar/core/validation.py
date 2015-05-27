from jsonschema import validate, ValidationError, SchemaError


def schema_input_type(schema):
    """Input type from schema

    :param schema:
    :return: simple/list
    """
    if isinstance(schema, list):
        return 'list'

    return 'simple'


def _construct_jsonschema(schema, definition_base=''):
    """Construct jsonschema from our metadata input schema.

    :param schema:
    :return:
    """
    if schema == 'str':
        return {'type': 'string'}, {}

    if schema == 'str!':
        return {'type': 'string', 'minLength': 1}, {}

    if schema == 'int' or schema == 'int!':
        return {'type': 'number'}, {}

    if isinstance(schema, list):
        items, definitions = _construct_jsonschema(schema[0], definition_base=definition_base)

        return {
            'type': 'array',
            'items': items,
        }, definitions

    if isinstance(schema, dict):
        properties = {}
        definitions = {}

        for k, v in schema.items():
            if isinstance(v, dict) or isinstance(v, list):
                key = '{}_{}'.format(definition_base, k)
                properties[k] = {'$ref': '#/definitions/{}'.format(key)}
                definitions[key], new_definitions = _construct_jsonschema(v, definition_base=key)
            else:
                properties[k], new_definitions = _construct_jsonschema(v, definition_base=definition_base)

            definitions.update(new_definitions)

        required = [k for k, v in schema.items() if
                    isinstance(v, basestring) and v.endswith('!')]

        ret = {
            'type': 'object',
            'properties': properties,
        }

        if required:
            ret['required'] = required

        return ret, definitions


def construct_jsonschema(schema):
    jsonschema, definitions = _construct_jsonschema(schema)

    jsonschema['definitions'] = definitions

    return jsonschema


def validate_input(value, jsonschema=None, schema=None):
    """Validate single input according to schema.

    :param value: Value to be validated
    :param schema: Dict in jsonschema format
    :param schema: Our custom, simplified schema
    :return: list with errors
    """
    if jsonschema is None:
        jsonschema = construct_jsonschema(schema)
    try:
        validate(value, jsonschema)
    except ValidationError as e:
        return [e.message]
    except:
        print 'jsonschema', jsonschema
        print 'value', value
        raise


def validate_resource(r):
    """Check if resource inputs correspond to schema.

    :param r: Resource instance
    :return: dict, keys are input names, value is array with error.
    """
    ret = {}

    input_schemas = r.metadata['input']
    args = r.args_dict()

    for input_name, input_definition in input_schemas.items():
        errors = validate_input(
            args.get(input_name),
            jsonschema=input_definition.get('jsonschema'),
            schema=input_definition.get('schema')
        )
        if errors:
            ret[input_name] = errors

    return ret