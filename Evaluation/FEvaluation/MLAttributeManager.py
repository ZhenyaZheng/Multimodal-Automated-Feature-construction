import os
from properties.properties import theproperty
from logger.logger import logger

class MLAttributeManager:
    def __init__(self):
        pass

    def getBackClassificationModel(self,datadict,includeValueBased = True):
        backgroundFilePath = self.getBackgroundFilePath(datadict, includeValueBased)
        path = backgroundFilePath

        # If the classification model already exists, load and return it
        if os.path.isfile(path):
            logger.Info("Background model already exists. Extracting from " + path)
            return self.getClassificationModel(datadict, backgroundFilePath)

        # Otherwise, generate, save and return it (WARNING - takes time)
        else:
            logger.Info("Background model doesn't exist for dataset " + datadict.name + ". Creating it...")

            # We begin by getting a list of all the datasets that need to participate in the creation of the background model
            self.generateMetaFeaturesInstances(includeValueBased)

            candidateAtrrDirectories = self.getDirectoriesInFolder(theproperty.DatasetInstancesFilesLocation)
            self.generateBackgroundARFFFileForDataset(datadict, backgroundFilePath, candidateAtrrDirectories,
                                                      includeValueBased)

            # now we load the contents of the ARFF file into an Instances object and train the classifier
            data = self.getInstancesFromARFF(backgroundFilePath)
            return self.buildClassifierModel(backgroundFilePath, data)