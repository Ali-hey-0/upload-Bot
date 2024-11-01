
## imghdr

 [![Build Status](https://api.travis-ci.org/meituan/imghdr.svg)](http://travis-ci.org/meituan/imghdr)
 [![NPM Version](http://img.shields.io/npm/v/imghdr.svg?style=flat)](https://www.npmjs.org/package/imghdr)
 [![NPM Downloads](https://img.shields.io/npm/dm/imghdr.svg?style=flat)](https://www.npmjs.org/package/imghdr)

> The `imghdr` module determines the type of image contained in a file or octet-streams(object of Buffer), inspired by Python's [imghdr](https://docs.python.org/3.4/library/imghdr.html) module.

## Installation

    npm install imghdr

## Usage
```javascript
var imghdr = require('imghdr');

var imgPath = __dirname + '/meituan.jpg';
var ext = 'jpg';

var exts = imghdr.what(imghdr);
console.log(exts);
// => ['jpg', 'jpeg']

if (exts.indexOf(ext) === -1) {
    console.log('The `' + imgPath + '`\'s extension is not a `' + ext + '`');
} else {
    console.log('OK');
}
// => 'OK'
```

## API
The `imghdr` module defines the following function:
### imghdr.what(imgPath)
>Tests the image data contained in the file named by `imgPath`, and returns an array of strings describing the image type. `imgPath` can be a object of [Buffer](http://nodejs.org/api/buffer.html).

|  Value |            Image format           |
|:------:|:---------------------------------:|
| "png"  | Portable Network Graphics         |
| "jpeg","jpg" | JPEG data in JFIF or Exif formats |
| "gif"  | GIF 87a and 89a Files             |
| "tiff" | Tagged Image File Format          |
| "bmp"  | BMP files                         |
| "webp" | WebP files                        |


You can extend the list of file types `imghdr` can recognize by appending to this variable:
### imghdr.tests
>A list of functions performing the individual tests. Each function takes a argument: the octet-streams(object of Buffer).The test function should return an array of strings describing the image type if the test succeeded, or `[]` if it failed.

Example:
```javascript
function testCustom(buf) {
    var sigBuf = new Buffer([0x6c, 0x6f, 0x76, 0x65]);
    var testSigBuf = buf.slice(2, 6);

    return (sigBuf.toString() == testSigBuf.toString()) ? ['custom'] : [];
}

// add to list of `tests`
imghdr.tests.push(testCustom);

var testBuf = new Buffer([0x49, 0x20, 0x6c, 0x6f, 0x76, 0x65, 0x20, 0x79, 0x6f, 0x75]);
imghdr.what(testBuf);
// => ['custom']
```

## Reference
- [http://www.filesignatures.net](http://www.filesignatures.net/index.php?page=all)
- <http://www.garykessler.net/library/file_sigs.html>
- <https://docs.python.org/3.4/library/imghdr.html>

## LICENSE

MIT
