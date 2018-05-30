"""testPiv mode asynchrone
================
"""
import os
import time
import multiprocessing
import functools
import scipy.io
import asyncio

from fluidimage.topologies.piv import TopologyPIV
from fluidimage.util.util import imread
from fluidimage.works.piv.multipass import WorkPIV
from fluidimage.data_objects.piv import ArrayCouple


class AsyncPiv:

    def __init__(self, path_image, path_save):
        self.path_images = path_image
        self.path_save = path_save
        self.img_tmp = None

    async def process(self, im1, im2):
        """
        this function call get image, compute piv;  and save piv
        :param index_image: index of images to compute
        :param path: path of images to compute
        :return: none
        """
        start = time.time()
        couple = await self.load_images(im1, im2)
        result = await self.compute(couple)
        light_result = result.make_light_result()
        await self.save_pib(light_result, im1, im2)
        end = time.time()
        print("Computing image {}: {}".format(im1 + " - " + im2, end - start))
        return

    async def load_images(self, im1, im2):
        """
        load two image and make a couple
        :param index_image:
        :param path: path to find images to compute
        :return: couple
        """
        if self.img_tmp == None:
            image1 = await self.loop.run_in_executor(
                None, functools.partial(imread, self.path_images + im1)
            )
        else:
            image1 = self.img_tmp

        image2 = await self.loop.run_in_executor(
            None, functools.partial(imread, self.path_images + im2)
        )
        params_mask = self.params.mask
        couple = ArrayCouple(
            names=(im1, im2), arrays=(image1, image2), params_mask=params_mask
        )
        self.img_tmp = image2
        return couple

    async def compute(self, couple):
        """
        Create a pivwork and compute a couple
        :param couple: a couple from arrayCouple
        :return: a piv object
        """
        workpiv = WorkPIV(self.params)
        return workpiv.calcul(couple)

    async def save_pib(self, light_result, im1, im2):
        im1 = im1[:-4]
        im2 = im2[:-4]
        scipy.io.savemat(
            self.path_save + "piv_" + im1 + "_" + im2,
            mdict={
                "deltaxs": light_result.deltaxs,
                "deltays": light_result.deltays,
                "xs": light_result.xs,
                "ys": light_result.ys,
            },
        )

    def a_process(self, listdir):
        """
        Define a concurenced work which is destined to be compute in one process
        :param i: will be changed later, allow to choose a set of images
        :return:
        """
        self.params = TopologyPIV.create_default_params()
        self.params.series.path = path
        self.params.series.ind_start = 1

        self.params.piv0.shape_crop_im0 = 32
        self.params.multipass.number = 2
        self.params.multipass.use_tps = True

        self.params.multipass.use_tps = True

        # params.saving.how has to be equal to 'complete' for idempotent jobs
        self.params.saving.how = "complete"
        self.params.saving.postfix = "piv_complete_async"

        self.loop = asyncio.get_event_loop()

        tasks = []
        for i in range(len(listdir) - 1):
            tasks.append(
                asyncio.ensure_future(self.process(listdir[i], listdir[i + 1]))
            )
        self.loop.run_until_complete(asyncio.wait(tasks))
        self.loop.close()


if __name__ == "__main__":
    # Managing dir paths
    sub_path_image = "Images"
    path = "../../image_samples/Karman/{}/".format(sub_path_image)
    path_save = "../../image_samples/Karman/{}.results.async/".format(sub_path_image)
    if not os.path.exists(path_save):
        os.makedirs(path_save)

    def partition(lst, n):
        """
        partition evently lst into n sublists and
        add the last images of each sublist to the head
        of the next sublist ( in order to compute all piv )
        :param lst: a list
        :param n: number of sublist wanted
        :return:
        """
        L = len(lst)
        assert 0 < n <= L
        s, r = divmod(L, n)
        t = s + 1
        lst = [lst[p : p + t] for p in range(0, r * t, t)] + [
            lst[p : p + s] for p in range(r * t, L, s)
        ]
        #  in order to compute all piv
        #  add the last images of each sublist to the head of the next sublist
        for i in range(1, n):
            lst[i].insert(0, lst[i - 1][-1])
        return lst

    nb_process = multiprocessing.cpu_count()
    # spliting images list
    listdir = os.listdir(path)
    if len(listdir) <= nb_process:  # if there is less piv to compute than cpu
        nb_process = len(listdir) - 1  # adapt process number
    print("nb process :{}".format(nb_process))
    listdir.sort()
    listdir = partition(listdir, nb_process)
    # making and starting processes
    processes = []
    pool = multiprocessing.Pool(processes=nb_process)
    for i in range(nb_process):
        async = AsyncPiv(path, path_save)
        p = multiprocessing.Process(target=async.a_process, args=(listdir[i],))
        p.start()
    for p in processes:
        p.join()