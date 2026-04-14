# -*- coding: utf-8 -*-
from pkg_resources import get_distribution, DistributionNotFound

try:
    # Change here if project is renamed and does not equal the package name
    dist_name = 'vendor-rewards-processor'
    __package_name__ = dist_name
    __version__ = get_distribution(dist_name).version
except DistributionNotFound:
    __version__ = 'unknown'

package_name = __package_name__
package_version = __version__


