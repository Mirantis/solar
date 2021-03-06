#    Copyright 2015 Mirantis, Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from solar.dblayer.model import Field
from solar.dblayer.model import Model
from solar.dblayer.model import NestedField
from solar.dblayer.model import NestedModel


class N1(NestedModel):

    f_nested1 = Field(str)
    f_nested2 = Field(int, default=150)


class M1(Model):

    f1 = Field(str)
    f2 = NestedField(N1)
    f3 = NestedField(N1, hash_key='f_nested1')


def test_nested_simple(rk):

    key = next(rk)

    m1 = M1.from_dict(key, {'f1': 'blah', 'f2': {'f_nested1': 'foo'}})

    assert m1.f2.f_nested1 == 'foo'
    assert m1.f2.f_nested2 == 150
    assert m1._modified_fields == set(['f1', 'f2'])
    assert m1._data_container == {'f1': 'blah',
                                  'f2': {'f_nested1': 'foo',
                                         'f_nested2': 150}}
    del m1.f2
    assert m1._data_container == {'f1': 'blah'}


def test_nested(rk):
    key = next(rk)

    m1 = M1.from_dict(key, {'f1': 'blah',
                            'f2': {'f_nested1': 'foo'},
                            'f3': {'f_nested1': 'foo',
                                   'f_nested2': 150}})

    assert m1.f2.f_nested1 == 'foo'
    assert m1.f2.f_nested2 == 150
    assert m1.f3['foo'].f_nested2 == 150

    m1.f3['blah'].f_nested2 = 250

    assert m1.f3['foo'].f_nested2 == 150
    assert m1.f3['blah'].f_nested2 == 250
    assert m1._modified_fields == set(['f1', 'f2', 'f3'])

    exp = {'f1': 'blah',
           'f2': {'f_nested1': 'foo',
                  'f_nested2': 150},
           'f3': {'blah': {'f_nested2': 250},
                  'foo': {'f_nested1': 'foo',
                          'f_nested2': 150}}}
    assert m1._data_container == exp

    del m1.f2
    exp.pop('f2')
    assert m1._data_container == exp

    assert m1._modified_fields == set(['f1', 'f2', 'f3'])
