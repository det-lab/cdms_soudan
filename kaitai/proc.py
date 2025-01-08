import awkward_kaitai
from pprint import pprint

soudan = awkward_kaitai.Reader("./libsoudan.so")
awkward_array = soudan.load("../minimal_sample.soudan")

pprint(awkward_array.to_list())
