/**
 * \file components/gpp/phy/Dvbt1Puncturer/benchmark/Dvbt1PuncturerComponent_benchmark.cpp
 * \version 0.1
 *
 * \section COPYRIGHT
 *
 * Copyright 2012-2016 The Iris Project Developers. See the
 * COPYRIGHT file at the top-level directory of this distribution
 * and at http://www.softwareradiosystems.com/iris/copyright.html.
 *
 * \section LICENSE
 *
 * This file is part of the Iris Project.
 *
 * Iris is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Lesser General Public License as
 * published by the Free Software Foundation, either version 3 of
 * the License, or (at your option) any later version.
 *
 * Iris is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Lesser General Public License for more details.
 *
 * A copy of the GNU Lesser General Public License can be found in
 * the LICENSE file in the top-level directory of this distribution
 * and at http://www.gnu.org/licenses/.
 *
 * \section DESCRIPTION
 *
 * Main benchmark file for Dvbt1Puncturer component.
 */

#include "../Dvbt1PuncturerComponent.h"
#include <boost/date_time/posix_time/posix_time.hpp>
#include <boost/random/mersenne_twister.hpp>
#include <boost/random/uniform_int.hpp>
#include "utility/DataBufferTrivial.h"
#include "utility/RawFileUtility.h"

using namespace std;
using namespace iris;
using namespace iris::phy;
namespace bp = boost::posix_time;

int main(int argc, char* argv[])
{
  int codearr[] = {12,23,34,56,78};
  string codenamearr[] = {"1/2","2/3","3/4","5/6","7/8"};

  for(int cri = 0; cri < sizeof(codearr) / sizeof(codearr[0]); cri++)
  {
    Dvbt1PuncturerComponent mod("test");
    mod.setValue("coderate", codearr[cri]);
    mod.registerPorts();

    map<string, int> iTypes,oTypes;
    iTypes["input1"] = TypeInfo< uint8_t >::identifier;
    mod.calculateOutputTypes(iTypes,oTypes);

    DataBufferTrivial< uint8_t > in;
    DataBufferTrivial< uint8_t > out;

    DataSet< uint8_t >* iSet = NULL;
    int num = 8*204*(10000000/204); // bits
    in.getWriteData(iSet, num);
    boost::random::mt19937 rng;
    boost::random::uniform_int_distribution<> two(0,1);
    for(int i=0;i<num;i++)
        iSet->data[i] = uint8_t(two(rng)); // random data
    in.releaseWriteData(iSet);

    mod.setBuffers(&in,&out);
    mod.initialize();

    bp::ptime t1(bp::microsec_clock::local_time());
    mod.process();
    bp::ptime t2(bp::microsec_clock::local_time());
    bp::time_duration time = t2-t1;

    float bitsPerSec = ((num)/(1.0e-9 * time.total_nanoseconds()));
    cout << codenamearr[cri] << ": Rate = " << bitsPerSec*1.0e-6 << " Mb/s" << endl;

    float maxRate = 31.67e6 * (204.0 / 188.0) * 2.0; // table A.1 pag. 40
    cout << "Maximum conv. encoded bit rate in ETSI EN 300 744 is " << maxRate*1.0e-6 << " Mb/s" << endl;

    if(bitsPerSec > 1.2 * maxRate)
      cout << "    >>>> " << bitsPerSec/maxRate << "x: GOOD! <<<<" << endl;
    else
      cout << "    >>>> " << bitsPerSec/maxRate << "x: OOPS! <<<<" << endl;
  }
}

