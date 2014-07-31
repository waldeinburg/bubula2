# Bubula² source

This is the source code of the [Bubula² website](http://bubula2.com) by Daniel Lundsgaard Skovenborg, <waldeinburg@bubula2.com>.
The source tree is a [Django](http://djangoproject.com) project, including deployment scripts. Though the project does not (at least not yet) aim to be a general system for webcomics, it may with some modifications be used as such.

The current state of the code is a bit peculiar because I until recently did not use version control. Therefore you may find functions that are not used on the Bubula² website yet and not fully implemented. I'm currently working on a cleanup.

The file settings.py is the one used on my local copy. For security reasons you can of course not get the online version. Likewise, fabconfig-dummy.yaml is a version of my fabconfig.yaml stripped for sensitive information.

The deployment script is for the [Fabric fork](https://github.com/traviscline/fabric) by [tav](http://tav.espians.com/fabric-python-with-cleaner-api-and-parallel-deployment-support.html). Thanks to [Ask The Pony](http://www.askthepony.com)!


## Licenses

**Notice**: The app hvadcontentblock is a mod of django-contentblock <https://github.com/divio/django-contentblock>.


### Source code

Copyright (c) 2012 Daniel Lundsgaard Skovenborg <waldeinburg@bubula2.com>

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.



### Artwork and content

Creative Commons Attribution-NonCommercial-NoDerivs 3.0 Unported License.
<http://creativecommons.org/licenses/by-nc-nd/3.0/deed.en_US>



### FreeSerifBubula2 font (bubula2/base/static/fonts/)

The font is the FreeSerif font with all glyphs removed, except the mathematical fracture glyphs for the word Bubula (and a few glyphs that, when removed, made FontForge crash on export for some reason).
The original font was obtained from <http://ftp.gnu.org/gnu/freefont/freefont-woff-20120503.zip>
[GPLv3](http://www.gnu.org/licenses/gpl-3.0.txt)

#### License

Free UCS scalable fonts is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License as published
by the Free Software Foundation; either version 3 of the License, or
(at your option) any later version.

The fonts are distributed in the hope that they will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License
for more details.

You should have received a copy of the GNU General Public License along
with this program; if not, write to the Free Software Foundation, Inc.,
51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.

As a special exception, if you create a document which uses this font, and
embed this font or unaltered portions of this font into the document, this
font does not by itself cause the resulting document to be covered by the
GNU General Public License. This exception does not however invalidate any
other reasons why the document might be covered by the GNU General Public
License. If you modify this font, you may extend this exception to your
version of the font, but you are not obligated to do so.  If you do not
wish to do so, delete this exception statement from your version.
