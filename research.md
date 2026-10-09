---
title: "Research"
permalink: /research/
---
# Research

CORE uses control and optimization to improve renewable energy harvesting and energy efficiency. The research areas below follow the existing university website.

<div class="research-grid">
{% for area in site.data.research %}<article class="project"><span class="number">{{ area.label }}</span><h2>{{ area.title }}</h2><p>{{ area.summary }}</p><a href="{{ area.path | relative_url }}">Explore this research area →</a></article>{% endfor %}
</div>

## Platform documentation

The [lab manual]({{ site.docs_url | relative_url }}) collects build and experiment records for [SeaTrac SP-48]({{ site.docs_url | append: 'seatrac-sp48/' | relative_url }}), the [Energy-Harvesting Kite]({{ site.docs_url | append: 'energy-harvesting-kite/' | relative_url }}), and [Saildrone]({{ site.docs_url | append: 'saildrone/' | relative_url }}).

Source: [Original research overview](https://corelab.engin.umich.edu/research/).
