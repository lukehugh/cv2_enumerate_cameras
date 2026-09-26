#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <vector>
#include <string>
#include <iostream>
#include <mfidl.h>
#include <mfapi.h>
#include <dshow.h>

#pragma comment(lib, "oleaut32")
#pragma comment(lib, "ole32")
#pragma comment(lib, "mf")
#pragma comment(lib, "mfplat")
#pragma comment(lib, "strmiids")

struct CameraInfo
{
    std::wstring name;
    std::wstring path;
};

bool MSMF_enumerate_cameras(std::vector<CameraInfo>& camera_info) {
    if (FAILED(CoInitializeEx(nullptr, COINIT_APARTMENTTHREADED)) && FAILED(CoInitializeEx(nullptr, COINIT_MULTITHREADED)))
        return false;
    if (FAILED(MFStartup(MF_VERSION)))
        return false;
    IMFAttributes* attr = nullptr;
    if (FAILED(MFCreateAttributes(&attr, 1)))
        return false;
    if (FAILED(attr->SetGUID(
        MF_DEVSOURCE_ATTRIBUTE_SOURCE_TYPE,
        MF_DEVSOURCE_ATTRIBUTE_SOURCE_TYPE_VIDCAP_GUID
    )))
        return false;
    IMFActivate** devices;
    UINT32 count;
    if (FAILED(MFEnumDeviceSources(attr, &devices, &count)))
        return false;
    attr->Release();

    camera_info.clear();
    for (UINT32 i = 0; i < count; ++i) {
        CameraInfo info;

        wchar_t* buffer = nullptr;
        if (SUCCEEDED(devices[i]->GetAllocatedString(
            MF_DEVSOURCE_ATTRIBUTE_FRIENDLY_NAME,
            &buffer,
            nullptr
        )) && buffer) {
            info.name = buffer;
            CoTaskMemFree(buffer);
            buffer = nullptr;
        }

        if (SUCCEEDED(devices[i]->GetAllocatedString(
            MF_DEVSOURCE_ATTRIBUTE_SOURCE_TYPE_VIDCAP_SYMBOLIC_LINK,
            &buffer,
            nullptr
        )) && buffer) {
            info.path = buffer;
            CoTaskMemFree(buffer);
            buffer = nullptr;
        }

        camera_info.emplace_back(info);
    }

    if (devices)
    {
        for (UINT32 i = 0; i < count; ++i)
            if (devices[i])
                devices[i]->Release();
        CoTaskMemFree(devices);
    }
    CoUninitialize();
    return true;
}

bool DSHOW_enumerate_cameras(std::vector<CameraInfo>& camera_info) {
    if (FAILED(CoInitializeEx(nullptr, COINIT_APARTMENTTHREADED)) && FAILED(CoInitializeEx(nullptr, COINIT_MULTITHREADED)))
        return false;

    ICreateDevEnum* pDevEnum = NULL;
    IEnumMoniker* pEnum = NULL;
    int deviceCounter = 0;

    HRESULT hr = CoCreateInstance(CLSID_SystemDeviceEnum, NULL,
        CLSCTX_INPROC_SERVER, IID_ICreateDevEnum,
        reinterpret_cast<void**>(&pDevEnum));


    if (SUCCEEDED(hr))
    {
        hr = pDevEnum->CreateClassEnumerator(
            CLSID_VideoInputDeviceCategory,
            &pEnum, 0);

        if (hr == S_OK) {

            IMoniker* pMoniker = NULL;

            while (pEnum->Next(1, &pMoniker, NULL) == S_OK) {
                CameraInfo info;

                IPropertyBag* pPropBag;
                hr = pMoniker->BindToStorage(0, 0, IID_IPropertyBag,
                    (void**)(&pPropBag));

                if (FAILED(hr)) {
                    pMoniker->Release();
                    continue;
                }

                VARIANT varName;
                VariantInit(&varName);
                hr = pPropBag->Read(L"Description", &varName, 0);

                if (FAILED(hr)) hr = pPropBag->Read(L"FriendlyName", &varName, 0);

                if (SUCCEEDED(hr)) {

                    if (SUCCEEDED(pPropBag->Read(L"FriendlyName", &varName, 0)))
                        info.name = varName.bstrVal;
                    if (SUCCEEDED(pPropBag->Read(L"DevicePath", &varName, 0)))
                        info.path = varName.bstrVal;
                }

                VariantClear(&varName);
                camera_info.push_back(info);

                pPropBag->Release();
                pPropBag = NULL;

                pMoniker->Release();
                pMoniker = NULL;

                deviceCounter++;
            }

            pDevEnum->Release();
            pDevEnum = NULL;

            pEnum->Release();
            pEnum = NULL;
        }
    }

    CoUninitialize();
    return true;
}

static PyObject* windows_backend_MSMF_enumerate_cameras(PyObject* self, PyObject* args)
{
    std::vector<CameraInfo> camera_info;
    bool success;
    Py_BEGIN_ALLOW_THREADS
    success = MSMF_enumerate_cameras(camera_info);
    Py_END_ALLOW_THREADS
    if (!success)
        return Py_BuildValue("");
    PyObject* result = PyList_New(camera_info.size());
    for (int i = 0; i < camera_info.size(); ++i) {
        PyObject* pytmp = Py_BuildValue("(uu)", camera_info[i].name.c_str(), camera_info[i].path.c_str());
        PyList_SetItem(result, i, pytmp);
    }
    return result;
}

static PyObject* windows_backend_DSHOW_enumerate_cameras(PyObject* self, PyObject* args)
{
    std::vector<CameraInfo> camera_info;
    bool success;
    Py_BEGIN_ALLOW_THREADS
    success = DSHOW_enumerate_cameras(camera_info);
    Py_END_ALLOW_THREADS
    if (!success)
        return Py_BuildValue("");
    PyObject* result = PyList_New(camera_info.size());
    for (int i = 0; i < camera_info.size(); ++i) {
        PyObject* pytmp = Py_BuildValue("(uu)", camera_info[i].name.c_str(), camera_info[i].path.c_str());
        PyList_SetItem(result, i, pytmp);
    }
    return result;
}

static PyMethodDef windows_backend_methods[] = {
    {"MSMF_enumerate_cameras",  windows_backend_MSMF_enumerate_cameras, METH_NOARGS, "MSMF_enumerate_cameras"},
    {"DSHOW_enumerate_cameras",  windows_backend_DSHOW_enumerate_cameras, METH_NOARGS, "DSHOW_enumerate_cameras"},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef windows_backend_module = {
    PyModuleDef_HEAD_INIT,
    "_windows_backend",
    NULL,
    -1,
    windows_backend_methods
};

PyMODINIT_FUNC PyInit__windows_backend(void)
{
    PyObject* module = PyModule_Create(&windows_backend_module);
#ifdef Py_GIL_DISABLED
    if (module != nullptr)
        PyUnstable_Module_SetGIL(module, Py_MOD_GIL_NOT_USED);
#endif
    return module;
}
