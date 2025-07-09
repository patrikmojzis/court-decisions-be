# https://docs.pydantic.dev/2.7/api/config/#pydantic.config.ConfigDict.use_enum_values
default_model_config = {
    "str_strip_whitespace": True,
    "validate_assignment": True,  # whether to validate when data changed
    "from_attributes": True, # whether to build models and look up discriminators of tagged unions using python object attributes
    "use_enum_values": True,  # whether to populate models with the value property of enums, rather than the raw enum
    "extra": "ignore",  # ignore extra fields
    # "arbitrary_types_allowed": True,  # whether arbitrary types are allowed in models
}
