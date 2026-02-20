from typing import override

from osgeo import gdal  # pyright: ignore[reportMissingImports]
from pydantic import Field

from src.models.schemas import AlgorithmParamsBaseModel

from . import AlgorithmAbstractFactory, BaseAlgorithm


class VectorTransformAlgorithmParams(AlgorithmParamsBaseModel):
    """Pydantic-модель для параметров алгоритма трансформации векторных данных."""

    srs_def: str = Field(
        ..., description="Целевая система координат (например, 'EPSG:4326')"
    )
    s_srs: str | None = Field(
        default=None,
        description="Исходная система координат (необязательно, по умолчанию определяется автоматически)",
    )


@AlgorithmAbstractFactory.register_algorithm("VECTOR_TRANSFORM")
class VectorTransformAlgorithm(BaseAlgorithm[VectorTransformAlgorithmParams]):
    """Алгоритм для трансформации векторных данных."""

    def print_metadata(self, dataset: gdal.Dataset):
        """Выводит базовую метадату векторного изображения."""
        print("Basic metadata")
        # print("Bands count: %s" % dataset.RasterCount)
        # print("Data type: %s" % dataset.GetRasterBand(1).DataType)
        # print("Rows: %s | Cols: %s" % (dataset.RasterYSize, dataset.RasterXSize))
        # print("GeoTransform: %s" % str(dataset.GetGeoTransform()))
        print(
            "Coordinate reference system: %s"
            % dataset.GetProjection()[-len('  AUTHORITY["EPSG","4326"]') :]
        )

    @override
    def run(
        self,
        input_file_bytes: bytes,
        file_ext: str,
        params: VectorTransformAlgorithmParams,
    ) -> bytes:
        """Трансформирует растровые данные.

        Args:
            input_file_bytes (bytes): Байтовое представление входного файла.
        Returns:
            bytes: Байтовое представление выходного файла.
        """

        s_srs = params.s_srs
        srs_def = params.srs_def

        gdal.FileFromMemBuffer(f"/vsimem/in.{file_ext}", input_file_bytes)

        opts = gdal.VectorTranslateOptions(dstSRS=srs_def, srcSRS=s_srs)

        out_ds = gdal.VectorTranslate(
            f"/vsimem/out.{file_ext}", f"/vsimem/in.{file_ext}", options=opts
        )

        f = gdal.VSIFOpenL(f"/vsimem/out.{file_ext}", "rb")
        gdal.VSIFSeekL(f, 0, 2)
        size = gdal.VSIFTellL(f)
        gdal.VSIFSeekL(f, 0, 0)
        result_bytes = gdal.VSIFReadL(1, size, f)
        gdal.VSIFCloseL(f)

        in_ds = gdal.OpenEx(f"/vsimem/in.{file_ext}", gdal.OF_VECTOR)

        # cleanup
        gdal.Unlink(f"/vsimem/in.{file_ext}")
        gdal.Unlink(f"/vsimem/out.{file_ext}")
        if out_ds is not None:
            out_ds = None  # type: ignore[assignment]
        if in_ds is not None:
            in_ds = None  # type: ignore[assignment]

        return result_bytes

    @override
    @classmethod
    def get_pydantic_model(cls) -> type[VectorTransformAlgorithmParams]:
        """Возвращает Pydantic-модель для валидации параметров алгоритма.

        Returns:
            BaseModel: Pydantic-модель параметров алгоритма.
        """
        return VectorTransformAlgorithmParams
