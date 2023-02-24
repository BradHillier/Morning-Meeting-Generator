//
//  ContentViewswift
//  Morning Meeting Generator
//
//  Created by Brad Hillier on 2022-05-16.
//

import SwiftUI
import PythonKit

// Application Colour Scheme
let LightGray = Color(red: 248/255, green: 248/255, blue: 248/255)
let Gray = Color(red: 225/255, green: 225/255, blue: 225/255)
let DarkGray = Color(red: 102/255, green: 102/255, blue: 102/255)
let Orange = Color(red: 240/255, green: 90/255, blue: 26/255)
let DarkOrange = Color(red: 208/255, green: 26/255, blue: 8/255)


struct OrangeButton: ButtonStyle {
    func makeBody(configuration: Configuration) -> some View {
        configuration.label
            .padding()
            .foregroundColor(.white)
            .background(Orange)
            .border(DarkOrange)
            .clipShape(RoundedRectangle(cornerRadius: 3))
            .opacity(configuration.isPressed ? 0.9 : 1.0)

    }
}

func runPythonCode(){
  let sys = Python.import("sys")
  sys.path.append("../..//src/")
  let example = Python.import("main")
  let response = example.main()
  print(response)
}


struct ContentView: View {
    @State private var personal_access_token: String = ""
    @State private var output_location: String = ""
    
    @State private var showView = "NormalView"
    
    var body: some View {
        
        switch showView
        {
        case "NormalView":
            VStack() {
                Image("sealegs-logo")
                    .resizable()
                    .frame(width: 250,
                           height: 250)
                    .padding(.bottom, 5)
                Text("Morning Meeting Generator")
                    .font(.system(size: 22))
                    .foregroundColor(DarkGray)
                    .fontWeight(.bold)
                HStack() {
                    Button(action: {
                        runPythonCode()
                    }) {
                        Label("Generate Document", systemImage: "chevron.right")
                    }
                    Button(action: {
                        showView = "SettingsView"
                    }) {
                        Label("Settings", systemImage: "gearshape")
                    }
                }
                .padding(20)
                .buttonStyle(OrangeButton())
                .background(LightGray)
                .border(Gray)
            }
            .padding(50)
            .background(Color.white)
        case "SettingsView":
            VStack() {
                VStack() {
                    Text("TimeTree")
                        .font(.system(size: 22))
                        .foregroundColor(DarkGray)
                        .fontWeight(.bold)
                    HStack {
                        Text("Personal Access Token: ")
                            .foregroundColor(Color.black)

                        TextField("what", text: $personal_access_token)
                            .foregroundColor(Color.black)
                            .border(Gray)
                    }
                    HStack {
                        Text("Calendar ID: ")
                            .foregroundColor(Color.black)

                        TextField("what", text: $personal_access_token)
                            .foregroundColor(Color.black)
                    }
                }
                HStack {
                    Text("Output Location: ")
                        .foregroundColor(Color.black)

                    TextField("what", text: $output_location)
                        .foregroundColor(Color.black)
                }
                Button(action: {
                    showView = "NormalView"
                }) {
                    Label("Go Back", systemImage: "arrowshape.turn.up.backward")
                }
                .buttonStyle(OrangeButton())
            }
            .padding(50)
            .background(Color.white)
        default:
            Text("Should never reach this view")
        }
    }
}

struct ContentView_Previews: PreviewProvider {
    static var previews: some View {
        ContentView()
    }
}
