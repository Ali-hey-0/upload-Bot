/*jshint camelcase:false, node:true */
/**
 * Recognize image file formats based on their first few bytes.
 */
 'use strict';

var fs = require('fs');
var tests = [];

exports.tests = tests;

// 兼容0.11.14以下的node版本
// fork from https://raw.githubusercontent.com/substack/node-buffer-equal/master/index.js
function bufferEqual(a, b) {
    if (!Buffer.isBuffer(a)) return undefined;
    if (!Buffer.isBuffer(b)) return undefined;
    if (typeof a.equals === 'function') return a.equals(b);
    if (a.length !== b.length) return false;
    for (var i = 0; i < a.length; i++) {
        if (a[i] !== b[i]) return false;
    }
    return true;
};

/* Subroutines per image file type. */
// PNG Portable Network Graphics
function testPNG(buf) {
    var sigBuf = new Buffer([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);
    var len = sigBuf.length;
    var testSigBuf = buf.slice(0, len);

    return bufferEqual(testSigBuf, sigBuf) ? ['png'] : [];
}
tests.push(testPNG);

// JPEG data in `JFIF` or `Exif` format
function testJPEG(buf) {
    var sigBuf = new Buffer([0xff, 0xd8, 0xff]);

    var len = sigBuf.length;
    var testSigBuf = buf.slice(0, len);

    // JPEG
    if (!bufferEqual(testSigBuf, sigBuf)) return [];

    testSigBuf = buf.slice(6, 10);

    // JFIF
    var sigBufJFIF = new Buffer([0x4a, 0x46, 0x49, 0x46]);
    if (bufferEqual(testSigBuf, sigBufJFIF)) return ['jpg', 'jpeg'];

    // Exif
    var sigBufExif = new Buffer([0x45, 0x78, 0x69, 0x66]);
    if (bufferEqual(testSigBuf, sigBufExif)) return ['jpg', 'jpeg'];

    return [];
}
tests.push(testJPEG);

// GIF (`GIF87a` and `GIF89a` variants)
function testGIF(buf) {
    var sigBufSet = [
        new Buffer([0x47, 0x49, 0x46, 0x38, 0x39, 0x61]),
        new Buffer([0x47, 0x49, 0x46, 0x38, 0x37, 0x61]),
    ];

    for (var i = 0; i < sigBufSet.length; i++) {
        var sigBuf = sigBufSet[i];
        var len = sigBuf.length;
        var testSigBuf = buf.slice(0, len);
        if (bufferEqual(testSigBuf, sigBuf)) return ['gif'];
    }

    return [];
}
tests.push(testGIF);

// TIFF Tagged Image File Format
function testTIFF(buf) {
    var sigBufSet = [
        new Buffer([0x4D, 0x4D]),
        new Buffer([0x49, 0x49])
    ];
    for (var i = 0; i < sigBufSet.length; i++) {
        var sigBuf = sigBufSet[i];
        var len = sigBuf.length;
        var testSigBuf = buf.slice(0, len);
        if (bufferEqual(testSigBuf, sigBuf)) return ['tiff'];
    }

    return [];
}
tests.push(testTIFF);

// BMP
function testBMP(buf) {
    var sigBuf = new Buffer([0x42, 0x4d]);
    var len = sigBuf.length;
    var testSigBuf = buf.slice(0, len);

    return bufferEqual(testSigBuf, sigBuf) ? ['bmp'] : [];
}
tests.push(testBMP);

// WEBP
function testWEBP(buf) {
    var sigBufRIFF = new Buffer([0x52, 0x49, 0x46, 0x46]);
    var sigBufWEBP = new Buffer([0x57, 0x45, 0x42, 0x50]);

    var testSigBuf = buf.slice(0, 4);
    if (!bufferEqual(testSigBuf, sigBufRIFF)) return [];

    testSigBuf = buf.slice(8, 12);
    return bufferEqual(testSigBuf, sigBufWEBP) ? ['webp'] : [];
}
tests.push(testWEBP);

/**
 * 测试图片的后缀名是否准确
 * @param {String|Buffer} imgPath image file path or object of Buffer
 * @param {String} ext image file extension
 * @return 后缀名与图片的真实类型相同时返回true；否则，返回false。
 */
function assert(imgPath, ext) {
    var exts = what(imgPath);

    ext = ext.toLowerCase();

    return (exts.indexOf(ext) === -1) ? false : true;
}
exports.assert = assert;

/**
 * Recognize image headers
 * @param {String|Buffer} imgPath img file path or object of Buffer
 * @return {Array} 获取图片文件的真实类型可用后缀数组；如果无法识别则返回空数组。
 */
function what(imgPath) {
    var imgBuf;

    if (Buffer.isBuffer(imgPath)) {
        imgBuf = imgPath;
    } else {
        imgBuf = fs.readFileSync(imgPath, {flag: 'r'});
    }

    if(imgBuf.length <= 0) return [];

    for (var i = 0; i < tests.length; i++) {
        var test = tests[i];
        if (typeof test == 'function') {
            var exts = tests[i](imgBuf);
            if (exts.length) return exts;
        }
    }

    return [];
}

exports.what = what;
