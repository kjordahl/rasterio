import json
import logging
import sys

import click
from click.testing import CliRunner

import rasterio
from rasterio.rio import cli, info


logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)


def test_edit_nodata_err(data):
    runner = CliRunner()
    inputfile = str(data.join('RGB.byte.tif'))
    result = runner.invoke(info.edit, [inputfile, '--nodata', '-1'])
    assert result.exit_code == 2


def test_edit_nodata(data):
    runner = CliRunner()
    inputfile = str(data.join('RGB.byte.tif'))
    result = runner.invoke(info.edit, [inputfile, '--nodata', '255'])
    assert result.exit_code == 0
    with rasterio.open(inputfile) as src:
        assert src.nodata == 255.0


def test_edit_crs_err(data):
    runner = CliRunner()
    inputfile = str(data.join('RGB.byte.tif'))
    result = runner.invoke(info.edit, [inputfile, '--crs', 'LOL:WUT'])
    assert result.exit_code == 2


def test_edit_crs_epsg(data):
    runner = CliRunner()
    inputfile = str(data.join('RGB.byte.tif'))
    result = runner.invoke(info.edit, [inputfile, '--crs', 'EPSG:32618'])
    assert result.exit_code == 0
    with rasterio.open(inputfile) as src:
        assert src.crs == {'init': 'epsg:32618'}


def test_edit_crs_proj4(data):
    runner = CliRunner()
    inputfile = str(data.join('RGB.byte.tif'))
    result = runner.invoke(info.edit, [inputfile, '--crs', '+init=epsg:32618'])
    assert result.exit_code == 0
    with rasterio.open(inputfile) as src:
        assert src.crs == {'init': 'epsg:32618'}


def test_edit_crs_obj(data):
    runner = CliRunner()
    inputfile = str(data.join('RGB.byte.tif'))
    result = runner.invoke(
        info.edit, [inputfile, '--crs', '{"init": "epsg:32618"}'])
    assert result.exit_code == 0
    with rasterio.open(inputfile) as src:
        assert src.crs == {'init': 'epsg:32618'}


def test_edit_transform_err_not_json(data):
    runner = CliRunner()
    inputfile = str(data.join('RGB.byte.tif'))
    result = runner.invoke(info.edit, [inputfile, '--transform', 'LOL'])
    assert result.exit_code == 2


def test_edit_transform_err_bad_array(data):
    runner = CliRunner()
    inputfile = str(data.join('RGB.byte.tif'))
    result = runner.invoke(info.edit, [inputfile, '--transform', '[1,2]'])
    assert result.exit_code == 2


def test_edit_transform_affine(data):
    runner = CliRunner()
    inputfile = str(data.join('RGB.byte.tif'))
    input_t = '[300.038, 0.0, 101985.0, 0.0, -300.042, 2826915.0]'
    result = runner.invoke(info.edit, [inputfile, '--transform', input_t])
    assert result.exit_code == 0
    with rasterio.open(inputfile) as src:
        for a, b in zip(src.affine, json.loads(input_t)):
            assert round(a, 6) == round(b, 6)


def test_edit_transform_gdal(data):
    runner = CliRunner()
    inputfile = str(data.join('RGB.byte.tif'))
    input_t = '[300.038, 0.0, 101985.0, 0.0, -300.042, 2826915.0]'
    result = runner.invoke(info.edit, [
        inputfile,
        '--transform', '[101985.0, 300.038, 0.0, 2826915.0, 0.0, -300.042]'])
    assert result.exit_code == 0
    with rasterio.open(inputfile) as src:
        for a, b in zip(src.affine, json.loads(input_t)):
            assert round(a, 6) == round(b, 6)


def test_edit_tags(data):
    runner = CliRunner()
    inputfile = str(data.join('RGB.byte.tif'))
    result = runner.invoke(info.edit, [
        inputfile, '--tag', 'lol=1', '--tag', 'wut=2'])
    assert result.exit_code == 0
    with rasterio.open(inputfile) as src:
        assert src.tags()['lol'] == '1'
        assert src.tags()['wut'] == '2'

def test_env():
    runner = CliRunner()
    result = runner.invoke(info.env, ['--formats'])
    assert result.exit_code == 0
    assert 'GTiff' in result.output


def test_info_err():
    runner = CliRunner()
    result = runner.invoke(
        info.info,
        ['tests'])
    assert result.exit_code == 1


def test_info():
    runner = CliRunner()
    result = runner.invoke(
        info.info,
        ['tests/data/RGB.byte.tif'])
    assert result.exit_code == 0
    assert '"count": 3' in result.output


def test_info_verbose():
    runner = CliRunner()
    result = runner.invoke(
        cli.cli,
        ['-v', 'info', 'tests/data/RGB.byte.tif'])
    assert result.exit_code == 0


def test_info_quiet():
    runner = CliRunner()
    result = runner.invoke(
        cli.cli,
        ['-q', 'info', 'tests/data/RGB.byte.tif'])
    assert result.exit_code == 0


def test_info_count():
    runner = CliRunner()
    result = runner.invoke(
        info.info,
        ['tests/data/RGB.byte.tif', '--count'])
    assert result.exit_code == 0
    assert result.output == '3\n'


def test_info_nodatavals():
    runner = CliRunner()
    result = runner.invoke(
        info.info,
        ['tests/data/RGB.byte.tif', '--bounds'])
    assert result.exit_code == 0
    assert result.output == '101985.0 2611485.0 339315.0 2826915.0\n'


def test_info_tags():
    runner = CliRunner()
    result = runner.invoke(
        info.info,
        ['tests/data/RGB.byte.tif', '--tags'])
    assert result.exit_code == 0
    assert result.output == '{"AREA_OR_POINT": "Area"}\n'


def test_info_res():
    runner = CliRunner()
    result = runner.invoke(
        info.info,
        ['tests/data/RGB.byte.tif', '--res'])
    assert result.exit_code == 0
    assert result.output.startswith('300.037')


def test_info_lnglat():
    runner = CliRunner()
    result = runner.invoke(
        info.info,
        ['tests/data/RGB.byte.tif', '--lnglat'])
    assert result.exit_code == 0
    assert result.output.startswith('-77.757')


def test_mo_info():
    runner = CliRunner()
    result = runner.invoke(info.info, ['tests/data/RGB.byte.tif'])
    assert result.exit_code == 0
    assert '"res": [300.037' in result.output
    assert '"lnglat": [-77.757' in result.output


def test_info_stats():
    runner = CliRunner()
    result = runner.invoke(info.info, ['tests/data/RGB.byte.tif', '--tell-me-more'])
    assert result.exit_code == 0
    assert '"max": 255.0' in result.output
    assert '"min": 1.0' in result.output
    assert '"mean": 44.4344' in result.output


def test_info_stats_only():
    runner = CliRunner()
    result = runner.invoke(info.info, ['tests/data/RGB.byte.tif', '--stats', '--bidx', '2'])
    assert result.exit_code == 0
    assert result.output.startswith('1.000000 255.000000 66.02')
