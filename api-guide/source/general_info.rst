..
      Copyright 2014-2017 Fujitsu LIMITED

      Licensed under the Apache License, Version 2.0 (the "License"); you may
      not use this file except in compliance with the License. You may obtain
      a copy of the License at

          http://www.apache.org/licenses/LICENSE-2.0

      Unless required by applicable law or agreed to in writing, software
      distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
      WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
      License for the specific language governing permissions and limitations
      under the License.

========================
Monasca Log API Concepts
========================

The Monasca Log API is defined as a RESTful HTTP service. The API
takes advantage of all aspects of the HTTP protocol (methods, URIs,
media types, response codes, etc.) and providers are free to use
existing features of the protocol such as caching, persistent
connections, and content compression among others.

Providers can return information identifying requests in HTTP response
headers, for example, to facilitate communication between the provider
and client applications.

Monasca LOG is a service that provides log collection capabilities over cloud.

User Concepts
=============

To use the Monasca Log API effectively, you should understand several
key concepts:

- **Log**

- **Dimensions**

Relationship with Metric API
============================

The Monasca Log API follow similar concept as Monasca Metric API.
Both are using the same meta-like language to describie entities that are
sent over wire. Below list enumerates those meta properties:

- dimensions
- meta_value
