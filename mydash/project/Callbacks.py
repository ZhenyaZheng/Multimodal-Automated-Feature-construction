import os

import dash
import numpy as np
import pandas as pd
from dash.dependencies import Input, Output, State, ClientsideFunction
import dask.dataframe as dd
from logger.logger import logger
from properties.properties import theproperty
from server import app
from Dataset import Dataset
from utils import generateModelData
from FeatureConstruction import FC
from FeatureConstruction import generateTestData
import plotly.graph_objects as go
import plotly.express as px

@app.callback(
    Output('setting2', 'children'),
    Input('start2', 'n_clicks'),
    # [State('maxevaluationattsperiter', 'value'),
    #  State('DiscretizerBinsNumber', 'value'),
    #  State('finalchosenopspath', 'value'),
    #  State('backmodelpath', 'value')],
    prevent_initial_call=True
)
def my_call(n_clicks):
    proprint()
    return "OK"


def setproperty(maxevaluationattsperiter, DiscretizerBinsNumber, finalchosenopspath, maxFEvaluationnums,
                     backmodelpath, datasetlocation, resultfilepath, dataframe, temppath, wrapper, classifier, thread,
                     fsocre, wsocre):
    theproperty.maxevaluationattsperiter = maxevaluationattsperiter
    theproperty.DiscretizerBinsNumber = DiscretizerBinsNumber
    theproperty.finalchosenopspath = finalchosenopspath
    theproperty.maxFEvaluationnums = maxFEvaluationnums
    theproperty.backmodelpath = backmodelpath
    theproperty.datasetlocation = datasetlocation
    theproperty.resultfilepath = resultfilepath
    theproperty.temppath = temppath
    theproperty.dataframe = dataframe
    theproperty.wrapper = wrapper
    theproperty.classifier = classifier
    theproperty.thread = thread
    theproperty.fsocre = fsocre
    theproperty.wsocre = wsocre


def proprint():
    print(theproperty.maxevaluationattsperiter)
    print(theproperty.DiscretizerBinsNumber)
    print(theproperty.finalchosenopspath)
    print(theproperty.backmodelpath)
    print(theproperty.datasetlocation)
    print(theproperty.resultfilepath)
    print(theproperty.temppath)
    print(theproperty.wrapper)
    print(theproperty.classifier)
    print(theproperty.thread)
    print(theproperty.fsocre)


@app.callback(
    Output('Pro_setting_out', 'children'),
    Input('Pro_setting', 'n_clicks'),
    [State('maxevaluationattsperiter', 'value'),
     State('DiscretizerBinsNumber', 'value'),
     State('finalchosenopspath', 'value'),
     State('maxFEvaluationnums', 'value'),
     State('backmodelpath', 'value'),
     State('datasetlocation', 'value'),
     State('resultfilepath', 'value'),
     State('dataframe', 'value'),
     State('temppath', 'value'),
     State('wrapper', 'value'),
     State('classifier', 'value'),
     State('thread', 'value'),
     State('fsocre', 'value'),
     State('wsocre', 'value'),
     ],
    prevent_initial_call=True
)
def setting_property(n_clicks, maxevaluationattsperiter, DiscretizerBinsNumber, finalchosenopspath, maxFEvaluationnums,
                     backmodelpath, datasetlocation, resultfilepath, dataframe, temppath, wrapper, classifier, thread,
                     fsocre, wsocre):
    setproperty(maxevaluationattsperiter, DiscretizerBinsNumber, finalchosenopspath, maxFEvaluationnums,
                     backmodelpath, datasetlocation, resultfilepath, dataframe, temppath, wrapper, classifier, thread,
                     fsocre, wsocre)
    #proprint()
    return "参数设置成功"

data = None
dataset = None
settingflag = False


@app.callback(
    Output('FC_settingdata_out', 'children'),
    Input('FC_settingdata', 'n_clicks'),
    [State('dataset_name', 'value'),
     State('image_path', 'value'),
     State('text_path', 'value'),
     State('tabular_path', 'value'),
     ],
    prevent_initial_call=True
)
def setting_dataset(n_clicks, name, image_path, text_path, tabular_path):

    if n_clicks >= 1:
        if image_path == "":
            image_path = None
        if text_path == "":
            text_path = None
        datapath = {"image_path": image_path, "text_path": text_path, "tabular_path": tabular_path}
        global dataset
        dataset = Dataset(datapath, name)
        global settingflag
        settingflag = True
        return "数据集设置成功"


@app.callback(
    Output('FC_GenerateData_out', 'children'),
    Input('FC_GenerateData', 'n_clicks'),
)
def mygeneratemodeldata(n_clicks):
    if n_clicks >= 1:
        global settingflag
        if settingflag is False:

            return "请先设置数据集"
        else:
            generateModelData(dataset)
            return "生成模型数据成功"



@app.callback(
    Output('FC_startFC', 'children'),
    Input('FC_strat', 'n_clicks'),
    [State('is_iter', 'value'),
     State('iternums', 'value'),
     State('oper_path', 'value'),
     State('image_oper', 'value'),
     State('text_oper', 'value'),
     State('oper_oper', 'value'),
     State('image_ign_oper', 'value'),
     State('text_ign_oper', 'value'),
     State('oper_ign_oper', 'value'),
     ],
    prevent_initial_call=True
)
def FC_dataset(n_clicks, is_iter, iternums, oper_path, image_oper, text_oper, oper_oper,
               image_ign_oper, text_ign_oper, oper_ign_oper):
    global dataset, settingflag
    if settingflag is False:
        return "数据集未设置"
    if n_clicks >= 1:
        if oper_path != "":
            if os.path.isfile(oper_path, 'r'):
                with open(oper_oper) as fp:
                    fp.read()
                eval(str(fp))
        selfoper = {"image": None, "text": None, "tabular": None}
        ignoper = {"image": None, "text": None, "tabular": None}
        if image_oper != "":
            selfoper["image"] = image_oper
        if text_oper != "":
            selfoper["text"] = text_oper
        if oper_oper != "":
            selfoper["tabular"] = oper_oper
        if image_ign_oper != "":
            ignoper["image"] = image_ign_oper
        if text_ign_oper != "":
            ignoper["text"] = text_ign_oper
        if oper_ign_oper != "":
            ignoper["tabular"] = oper_ign_oper
        global data
        data = FC(dataset, is_iter == 1, iternums, selfoper, ignoper)
        return "特征构建完成"


@app.callback(
    Output('FC_TestData_out', 'children'),
    Input('FC_TestData', 'n_clicks'),
    prevent_initial_call=True
)
def FC_TestData(n_clicks):

    if n_clicks >= 1:
        global dataset, settingflag
        if settingflag is False:
            return "数据集未设置"
        generateTestData(dataset)
        return "测试集特征构建完成"

@app.callback(
    [Output('dataview_table', 'data'),
    Output('dataview_table', 'columns'),
     Output('dataview_out', 'children')
     ],
    Input('datasetview-switch', 'value'),
)
def dataview_switch(value):
    try:
        #return None, None, "数据不存在！"
        if value == "原始数据":
            df = (dd.read_csv(
                theproperty.rootpath + theproperty.resultfilepath + theproperty.dataframe + theproperty.datasetname + "original/*.part")
                  if theproperty.dataframe == "dask" else pd.read_csv(
                theproperty.rootpath + theproperty.resultfilepath + theproperty.dataframe + theproperty.datasetname + "original/" + theproperty.dataframe + theproperty.datasetname + "original.csv"))
        elif value == '生成数据查看':
            df = pd.read_csv(theproperty.rootpath + theproperty.datasetlocation + theproperty.datasetname + "_candidatedata.csv")

        elif value == "训练集数据":
            df = (dd.read_csv(
                    theproperty.rootpath + theproperty.resultfilepath + theproperty.dataframe + theproperty.datasetname + "/*.part")
                if theproperty.dataframe == "dask" else pd.read_csv(
                    theproperty.rootpath + theproperty.resultfilepath + theproperty.dataframe + theproperty.datasetname + "/" + theproperty.dataframe + theproperty.datasetname + ".csv"))
        else:
            df = (dd.read_csv(
                theproperty.rootpath + theproperty.resultfilepath + theproperty.dataframe + theproperty.datasetname + "test/*.part")
                  if theproperty.dataframe == "dask" else pd.read_csv(
                theproperty.rootpath + theproperty.resultfilepath + theproperty.dataframe + theproperty.datasetname + "test/" + theproperty.dataframe + theproperty.datasetname + "test.csv"))
        df.insert(loc=0, column='#', value=df.index)
        return df.to_dict('records'), [{'name': column, 'id': column} for column in df.columns], "数据加载完成！"
    except Exception as ex:
        logger.Error(f"dataview_switch error: {ex}", ex)
        return None, None, "数据不存在！"


@app.callback(
    Output('dataresult-chart', 'figure'),
    [Input('data-result-switch', 'value'),
     Input('iteration_id', 'value'),]

)
def dataresult_switch_chart(value, iters):
    try:
        if value == '训练集结果':
            fig = go.Figure()
            df = pd.read_csv(theproperty.rootpath + theproperty.resultfilepath + theproperty.dataframe + theproperty.datasetname + "result.csv", index_col=False)
            namelist = str(df.loc[iters]["Added_Attributes"])
            LogLoss0 = float(df.loc[0]["LogLoss"])
            AUC0 = float(df.loc[0]["AUC"])
            F1Score0 = float(df.loc[0]["F1Score"])
            if len(namelist) > 2:
                namelist = namelist[1:-1].split('+')
            #namelist = [s[0:10] + "\n" + s[10:-1] if len(s) > 10 else s for s in namelist]
            #print(namelist)
            scorenamelist = ['AUC', 'LogLoss', 'F1Score']
            LogLoss = float(df.loc[iters]["LogLoss"])
            AUC = float(df.loc[iters]["AUC"])
            F1Score = float(df.loc[iters]["F1Score"])
            scorelist0 = [AUC0, LogLoss0, F1Score0]
            scorelist1 = [AUC, LogLoss, F1Score]
            Chosen_Attributes_FScore = str(df.loc[iters]["Chosen_Attributes_FScore"])
            if len(Chosen_Attributes_FScore) > 2:
                Chosen_Attributes_FScore = Chosen_Attributes_FScore[1:-2].split(',')
                Chosen_Attributes_FScore = [float(i) for i in Chosen_Attributes_FScore]
            Chosen_Attributes_WScore = str(df.loc[iters]["Chosen_Attributes_WScore"])
            if len(Chosen_Attributes_WScore) > 2:
                Chosen_Attributes_WScore = Chosen_Attributes_WScore[1:-2].split(',')
                Chosen_Attributes_WScore = [float(i) for i in Chosen_Attributes_WScore]
            fig.add_trace(go.Bar(
                y=namelist,
                x=Chosen_Attributes_FScore,
                name='FScore',
                marker_color='indianred',
                orientation='h'
            ))
            fig.add_trace(go.Bar(
                y=namelist,
                x=Chosen_Attributes_WScore,
                name='WScore',
                marker_color='lightsalmon',
                orientation='h'
            ))

            fig.update_layout(
                font=dict(
                    family="Times New Roman, SimSun",
                    size=7,
                )
            )

            fig.update_layout(
                title_font_family="Times New Roman, SimSun",
                autosize={'width':'100px', 'height':'100%'}
            )

            fig.update_layout(
                margin=dict(t=10, b=10)
            )
        else:
            fig = go.Figure()
            df = pd.read_csv(
                theproperty.rootpath + theproperty.resultfilepath + theproperty.dataframe + theproperty.datasetname + "testresult.csv", index_col=False)
            namelist = ['LogLoss', 'AUC', 'F1Score']
            LogLoss0 = float(df.loc[0]["LogLoss"])
            AUC0 = float(df.loc[0]["AUC"])
            F1Score0 = float(df.loc[0]["F1Score"])
            LogLoss1 = float(df.loc[1]["LogLoss"])
            AUC1 = float(df.loc[1]["AUC"])
            F1Score1 = float(df.loc[1]["F1Score"])
            scorelist0 = [AUC0, LogLoss0, F1Score0]
            scorelist1 = [AUC1, LogLoss1, F1Score1]
            fig.add_trace(go.Bar(
                y=namelist,
                x=scorelist0,
                name='Original_Score',
                marker_color='indianred',
                orientation='h'
            ))
            fig.add_trace(go.Bar(
                y=namelist,
                x=scorelist1,
                name='FC_Score'  ,
                marker_color='lightsalmon',
                orientation='h'
            ))
            fig.update_layout(
                font=dict(
                    family="Times New Roman, SimSun",
                    size=10
                )
            )

            fig.update_layout(
                title_font_family="Times New Roman, SimSun"
            )

            fig.update_layout(
                margin=dict(t=10, b=20)
            )



    except Exception as ex:
        logger.Error(f"dataresult_switch_chart error: {ex}", ex)
    finally:
        return fig


class Test:
    pass