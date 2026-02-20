from typing import override

from osgeo import gdal  # pyright: ignore[reportMissingImports]
from pydantic import Field

from src.models.schemas import AlgorithmParamsBaseModel

from . import AlgorithmAbstractFactory, BaseAlgorithm


class RasterRescaleAlgorithmParams(AlgorithmParamsBaseModel):
    """Pydantic-модель для параметров алгоритма изменения разрешения растровых данных."""

    xres: float = Field(
        description="Целевое разрешение по оси X (в единицах координатной системы)",
    )
    yres: float = Field(
        description="Целевое разрешение по оси Y (в единицах координатной системы)",
    )
    # square: bool | None = Field(
    #     None,
    #     description="Если True, сохранять пропорции пикселя при изменении разрешения",
    # )

    # @model_validator(mode="after")
    # def _validate_choice(self) -> "RasterRescaleAlgorithmParams":
    #     if self.square and (self.xres is None) and (self.yres is None):
    #         return self
    #     if (self.xres is None) or (self.yres is None) or (self.square is not None):
    #         raise ValueError(
    #             "Either 'square' must be True or both 'xres' and 'yres' must be provided"
    #         )
    #     return self


@AlgorithmAbstractFactory.register_algorithm("RASTER_RESCALE")
class RasterRescaleAlgorithm(BaseAlgorithm):
    """Алгоритм для изменения разрешения растровых данных."""

    def print_metadata(self, dataset: gdal.Dataset):
        """Выводит базовую метадату растрового изображения."""
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
    def run(self, input_file_bytes: bytes, file_ext: str) -> bytes:
        """Трансформирует растровые данные.

        Args:
            input_file_bytes (bytes): Байтовое представление входного файла.
        Returns:
            bytes: Байтовое представление выходного файла.
        """

        xres = self._params.xres  # type: ignore[attr-defined]
        yres = self._params.yres  # type: ignore[attr-defined]
        # square = self._params.square  # type: ignore[attr-defined]

        gdal.FileFromMemBuffer(f"/vsimem/in.{file_ext}", input_file_bytes)

        opts = gdal.WarpOptions(xRes=xres, yRes=yres)

        out_ds = gdal.Warp(
            f"/vsimem/out.{file_ext}", f"/vsimem/in.{file_ext}", options=opts
        )

        f = gdal.VSIFOpenL(f"/vsimem/out.{file_ext}", "rb")
        gdal.VSIFSeekL(f, 0, 2)
        size = gdal.VSIFTellL(f)
        gdal.VSIFSeekL(f, 0, 0)
        result_bytes = gdal.VSIFReadL(1, size, f)
        gdal.VSIFCloseL(f)

        in_ds: gdal.Dataset = gdal.Open(f"/vsimem/in.{file_ext}")
        self.print_metadata(in_ds)
        self.print_metadata(out_ds)

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
    def get_pydantic_model(cls) -> type[RasterRescaleAlgorithmParams]:
        """Возвращает Pydantic-модель для валидации параметров алгоритма.

        Returns:
            BaseModel: Pydantic-модель параметров алгоритма.
        """
        return RasterRescaleAlgorithmParams
