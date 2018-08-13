
def get_member(src, attr_name, args):
    obj = getattr(src, attr_name)
    if callable(obj):
        kw = {}
        for key, val in args.items():
            if val.startswith("[int]"):
                kw[key] = int(val[5:])
            elif val.startswith("[float]"):
                kw[key] = float(val[7:])
            elif val.startswith("[bool]"):
                kw[key] = val[6:].lower() == "true"
            else:
                kw[key] = val
        return obj(**kw)
    return obj


