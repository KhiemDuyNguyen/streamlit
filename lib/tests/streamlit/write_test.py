# -*- coding: utf-8 -*-
# Copyright 2018-2019 Streamlit Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Streamlit Unit test."""

from mock import call, patch, Mock
from collections import namedtuple

import time
import unittest

import numpy as np
import pandas as pd

import streamlit as st


class StreamlitWriteTest(unittest.TestCase):
    """Test st.write.

    Unit tests for https://streamlit.io/docs/api/text.html#streamlit.write

    Because we're going to test st.markdown, st.pyplot, st.altair_chart
    later on, we don't have to test it in st.write In st.write, all we're
    trying to check is that the right st.* method gets called
    """

    def test_string(self):
        """Test st.write with a string."""
        with patch("streamlit.markdown") as p:
            st.write("some string")

            p.assert_called_once()

        with patch("streamlit.markdown") as p:
            st.write("more", "strings", "to", "pass")

            p.assert_called_once_with("more strings to pass", unsafe_allow_html=False)

    def test_dataframe(self):
        """Test st.write with dataframe."""
        data = {
            "DataFrame": pd.DataFrame([[20, 30, 50]], columns=["a", "b", "c"]),
            "Series": pd.Series(np.array(["a", "b", "c"])),
            "Index": pd.Index(list("abc")),
            "ndarray": np.array(["a", "b", "c"]),
            "Styler": pd.DataFrame({"a": [1], "b": [2]}).style.format("{:.2%}"),
        }

        # Make sure we have test cases for all _DATAFRAME_LIKE_TYPES
        self.assertEqual(sorted(data.keys()), sorted(st._DATAFRAME_LIKE_TYPES))

        for df in data.values():
            with patch("streamlit.dataframe") as p:
                st.write(df)

                p.assert_called_once()

    def test_exception_type(self):
        """Test st.write with exception."""
        with patch("streamlit.exception") as p:
            st.write(Exception("some exception"))

            p.assert_called_once()

    def test_help(self):
        """Test st.write with help types."""
        # Test module
        with patch("streamlit.help") as p:
            st.write(np)

            p.assert_called_once()

        # Test function
        with patch("streamlit.help") as p:
            st.write(st.set_option)

            p.assert_called_once()

    @patch("streamlit.type_util.is_type")
    def test_altair_chart(self, is_type):
        """Test st.write with altair_chart."""
        is_type.return_value = True

        class FakeChart(object):
            pass

        with patch("streamlit.altair_chart") as p:
            st.write(FakeChart())

            p.assert_called_once()

    @patch("streamlit.type_util.is_type")
    def test_pyplot(self, is_type):
        """Test st.write with matplotlib."""
        is_type.side_effect = [False, True]

        class FakePyplot(object):
            pass

        with patch("streamlit.pyplot") as p:
            st.write(FakePyplot())

            p.assert_called_once()

    def test_plotly(self):
        import plotly.graph_objs as go

        """Test st.write with plotly object."""
        with patch("streamlit.plotly_chart") as p:
            st.write([go.Scatter(x=[1, 2], y=[10, 20])])

            p.assert_called_once()

    def test_dict(self):
        """Test st.write with dict."""
        with patch("streamlit.json") as p:
            st.write({"a": 1, "b": 2})

            p.assert_called_once()

    def test_list(self):
        """Test st.write with list."""
        with patch("streamlit.json") as p:
            st.write([1, 2, 3])

            p.assert_called_once()

    def test_namedtuple(self):
        """Test st.write with list."""
        with patch("streamlit.json") as p:
            Boy = namedtuple("Boy", ("name", "age"))
            John = Boy("John", 29)
            st.write(John)

            p.assert_called_once()

    @patch("streamlit.markdown")
    @patch("streamlit.json")
    def test_dict_and_string(self, mock_json, mock_markdown):
        """Test st.write with dict."""
        manager = Mock()
        manager.attach_mock(mock_json, "json")
        manager.attach_mock(mock_markdown, "markdown")

        st.write("here is a dict", {"a": 1, "b": 2}, " and that is all")

        expected_calls = [
            call.markdown("here is a dict", unsafe_allow_html=False),
            call.json({"a": 1, "b": 2}),
            call.markdown(" and that is all", unsafe_allow_html=False),
        ]
        self.assertEqual(manager.mock_calls, expected_calls)

    def test_default_object(self):
        """Test st.write with default clause ie some object."""

        class SomeObject(object):
            def __str__(self):
                return "1 * 2 - 3 = 4 `ok` !"

        with patch("streamlit.markdown") as p:
            st.write(SomeObject())

            p.assert_called_once_with(
                u"`1 * 2 - 3 = 4 \\`ok\\` !`", unsafe_allow_html=False
            )

    def test_exception(self):
        """Test st.write that raises an exception."""
        with patch("streamlit.markdown") as m, patch("streamlit.exception") as e:
            m.side_effect = Exception("some exception")
            st.write("some text")

            e.assert_called_once()

    def test_spinner(self):
        """Test st.spinner."""
        # TODO(armando): Test that the message is actually passed to
        # message.warning
        with patch("streamlit.empty") as e:
            with st.spinner("some message"):
                time.sleep(0.15)
            e.assert_called_once_with()
